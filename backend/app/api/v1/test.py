# app/api/v1/test.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import subprocess
import json
import os
import logging
from pathlib import Path
import re

router = APIRouter()
logger = logging.getLogger(__name__)


class TestRequest(BaseModel):
    modules: List[str]
    includePerformance: bool = False


class ModuleResult(BaseModel):
    moduleKey: str
    moduleName: str
    plannedCases: int
    executedCases: int
    passed: int
    failed: int
    skipped: int
    passRate: float
    completionScore: float
    qualityScore: float


class TestResponse(BaseModel):
    totalCases: int
    totalPassed: int
    totalFailed: int
    totalSkipped: int
    exitCode: int
    modules: List[ModuleResult]


MODULE_NAMES: Dict[str, str] = {
    "auth": "认证模块",
    "materials": "素材库模块",
    "ai": "AI生成模块",
    "adapter": "平台适配模块",
    "records": "创作记录模块",
    "statistics": "统计分析模块",
    "tags": "标签模块",
    "uploads": "上传服务",
    "dashboard": "仪表盘",
    "security": "安全测试",
    "performance": "性能测试",
}


def _count_test_functions(test_file: Path) -> int:
    """
    计划用例数：以测试文件中 def test_* 的数量为准（快速、直观，适配启动测试"验收完成度"展示）。
    
    注意：
    - 统计所有以 test_ 开头的函数
    - 不包括参数化测试的多个实例（pytest会自动处理）
    - 这是计划用例数，实际执行数可能因条件跳过而不同
    """
    if not test_file.exists():
        return 0
    try:
        content = test_file.read_text(encoding="utf-8")
        # 匹配 def test_xxx( 的模式
        test_functions = re.findall(r"^\s*def\s+(test_\w+)\s*\(", content, re.MULTILINE)
        return len(test_functions)
    except Exception:
        return 0


def _extract_module_key_from_nodeid(nodeid: str) -> Optional[str]:
    """
    从 pytest nodeid 提取模块 key：tests/test_xxx.py::test_yyy -> xxx
    """
    if not nodeid:
        return None
    # nodeid 在不同环境可能是 tests/test_xxx.py::... 或 tests\\test_xxx.py::...
    m = re.search(r"tests[\\/]+test_(?P<key>\w+)\.py::", nodeid)
    if not m:
        return None
    return m.group("key")


def _build_module_result(module_key: str, planned: int, stats: Dict[str, int]) -> Dict[str, Any]:
    executed = int(stats.get("executed", 0))
    passed = int(stats.get("passed", 0))
    failed = int(stats.get("failed", 0))
    skipped = int(stats.get("skipped", 0))

    pass_rate = (passed / executed * 100.0) if executed > 0 else 0.0
    completion = (executed / planned * 100.0) if planned > 0 else 0.0
    quality = pass_rate * 0.7 + completion * 0.3

    return {
        "moduleKey": module_key,
        "moduleName": MODULE_NAMES.get(module_key, module_key),
        "plannedCases": planned,
        "executedCases": executed,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "passRate": pass_rate,
        "completionScore": completion,
        "qualityScore": quality,
    }


@router.post("/test/run")
async def run_tests(request: TestRequest):
    """
    执行测试并返回结果
    """
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent.parent
        backend_dir = project_root / "backend"
        
        # 检查pytest是否安装
        try:
            import pytest
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="pytest未安装，请运行: pip install pytest pytest-json-report"
            )
        
        # includePerformance 或显式选择 performance 模块时，允许执行 slow/performance 用例
        selected_modules = list(dict.fromkeys(request.modules or []))  # 去重且保持顺序
        include_perf = bool(request.includePerformance) or ("performance" in selected_modules)
        if include_perf and "performance" not in selected_modules:
            selected_modules.append("performance")

        # 构建pytest命令 - 使用虚拟环境中的Python
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            # 如果Windows虚拟环境不存在，尝试Linux/Mac格式
            venv_python = backend_dir / "venv" / "bin" / "python"
        
        if venv_python.exists():
            # 使用虚拟环境中的Python执行pytest（正确方式）
            pytest_args = [
                str(venv_python),
                "-m",
                "pytest",
                "-v",
                "--json-report",
                "--json-report-file=test_report.json",
            ]
        else:
            # 回退到直接使用pytest命令
            pytest_args = [
                "pytest",
                "-v",
                "--json-report",
                "--json-report-file=test_report.json",
            ]

        # 默认不执行 slow（性能）用例；只有 include_perf=true 才放开
        if not include_perf:
            pytest_args.extend(["-m", "not slow"])
        
        # 根据选择的模块添加测试文件路径
        test_paths = []
        for module in selected_modules:
            test_file = backend_dir / f"tests/test_{module}.py"
            if test_file.exists():
                test_paths.append(str(test_file))
        
        if not test_paths:
            # 如果没有找到测试文件，使用所有测试
            test_dir = backend_dir / "tests"
            if test_dir.exists():
                test_paths.append(str(test_dir))
        
        if test_paths:
            pytest_args.extend(test_paths)
        else:
            logger.warning("未找到任何测试文件")
            raise HTTPException(
                status_code=400,
                detail="未找到指定的测试文件"
            )
        
        # 记录执行的pytest命令
        logger.info(f"执行pytest命令: {' '.join(pytest_args)}")
        logger.info(f"工作目录: {backend_dir}")
        
        # 执行pytest
        result = subprocess.run(
            pytest_args,
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            shell=False,
            encoding='utf-8',
            errors='replace'
        )
        
        # 记录pytest的输出
        if result.stdout:
            logger.info(f"pytest stdout:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"pytest stderr:\n{result.stderr}")
        logger.info(f"pytest退出码: {result.returncode}")
        
        # 读取测试报告（pytest-json-report）
        report_file = backend_dir / "test_report.json"
        summary: Dict[str, int] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        module_results: Dict[str, Dict[str, int]] = {}  # 按模块统计的测试结果（严格按 nodeid 归属）
        
        if report_file.exists():
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    # 解析pytest-json-report格式的报告
                    if "summary" in report_data:
                        summary = {
                            "total": int(report_data["summary"].get("total", 0) or 0),
                            "passed": int(report_data["summary"].get("passed", 0) or 0),
                            "failed": int(report_data["summary"].get("failed", 0) or 0),
                            "skipped": int(report_data["summary"].get("skipped", 0) or 0),
                        }
                        logger.info(f"测试结果汇总: {summary}")
                        
                        # 按模块统计测试结果
                        if "tests" in report_data:
                            for test_item in report_data["tests"]:
                                nodeid = test_item.get("nodeid", "")
                                outcome = test_item.get("outcome", "")
                                
                                module_key = _extract_module_key_from_nodeid(nodeid)
                                # 统计所有模块的测试结果，不仅仅是选中的模块
                                if not module_key:
                                    continue

                                if module_key not in module_results:
                                    module_results[module_key] = {"executed": 0, "passed": 0, "failed": 0, "skipped": 0}

                                module_results[module_key]["executed"] += 1
                                if outcome == "passed":
                                    module_results[module_key]["passed"] += 1
                                elif outcome == "failed":
                                    module_results[module_key]["failed"] += 1
                                elif outcome == "skipped":
                                    module_results[module_key]["skipped"] += 1
                        
                        logger.info(f"按模块统计结果: {module_results}")
                    else:
                        logger.warning(f"测试报告格式异常，缺少summary字段")
            except Exception as e:
                logger.error(f"读取测试报告失败: {e}", exc_info=True)
        else:
            logger.warning(f"测试报告文件不存在: {report_file}")
        
        # 计算模块级别的统计
        modules = []

        for module_key in selected_modules:
            test_file = backend_dir / f"tests/test_{module_key}.py"
            planned = _count_test_functions(test_file)
            stats = module_results.get(module_key, {"executed": 0, "passed": 0, "failed": 0, "skipped": 0})
            
            # 验证统计数据的一致性
            executed = stats.get("executed", 0)
            passed = stats.get("passed", 0)
            failed = stats.get("failed", 0)
            skipped = stats.get("skipped", 0)
            
            # 确保统计数据逻辑正确
            if executed != (passed + failed + skipped):
                logger.warning(
                    f"模块 {module_key} 的统计数据不一致: "
                    f"executed={executed}, passed={passed}, failed={failed}, skipped={skipped}"
                )
            
            modules.append(_build_module_result(module_key, planned, stats))
        
        # 验证总体统计数据的一致性
        total_executed = sum(m.get("executedCases", 0) for m in modules)
        total_passed = sum(m.get("passed", 0) for m in modules)
        total_failed = sum(m.get("failed", 0) for m in modules)
        total_skipped = sum(m.get("skipped", 0) for m in modules)
        
        if summary.get("total", 0) != total_executed:
            logger.warning(
                f"总体统计数据不一致: summary.total={summary.get('total', 0)}, "
                f"modules.total_executed={total_executed}"
            )
        
        logger.info(f"模块统计汇总: {modules}")
        
        # 返回符合前端期望的数据结构
        return {
            "data": {
                "totalCases": summary.get("total", 0),
                "totalPassed": summary.get("passed", 0),
                "totalFailed": summary.get("failed", 0),
                "totalSkipped": summary.get("skipped", 0),
                "exitCode": result.returncode,
                "modules": modules
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"执行测试失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"执行测试失败: {str(e)}"
        )


@router.get("/test/status")
async def get_test_status():
    """
    获取测试状态
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent.parent.parent
    backend_dir = project_root / "backend"
    tests_dir = backend_dir / "tests"
    
    # 检查测试文件是否存在
    test_files_exist = tests_dir.exists()
    if test_files_exist:
        # 检查是否有测试文件
        test_files = list(tests_dir.glob("test_*.py"))
        test_files_exist = len(test_files) > 0
    
    # 检查pytest是否安装
    pytest_installed = False
    try:
        import pytest
        pytest_installed = True
    except ImportError:
        pass
    
    return {
        "status": "ready",
        "pytest_installed": pytest_installed,
        "test_files_exist": test_files_exist
    }
