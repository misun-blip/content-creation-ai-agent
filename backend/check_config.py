#!/usr/bin/env python3
"""
配置检查脚本
用于验证项目配置是否正确，包括必需文件和配置项
"""

import sys
from pathlib import Path
import yaml

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def check_env_file():
    """检查.env文件"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    print_info("检查配置文件...")
    
    if not env_example_path.exists():
        print_warning(".env.example文件不存在")
    else:
        print_success(".env.example文件存在")
    
    if not env_path.exists():
        print_warning(".env文件不存在，将使用默认配置")
        print_info("提示: 可以复制.env.example为.env并修改配置")
        return False
    else:
        print_success(".env文件存在")
        return True

def check_platform_config():
    """检查平台配置文件"""
    config_path = Path("app/config/platform_config.yaml")
    
    print_info("检查平台配置文件...")
    
    if not config_path.exists():
        print_warning(f"平台配置文件不存在: {config_path}")
        print_info("将使用默认配置")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            print_error("平台配置文件为空")
            return False
        
        if 'platforms' not in config:
            print_error("平台配置文件缺少platforms字段")
            return False
        
        platforms = config.get('platforms', {})
        required_platforms = ['douyin', 'xiaohongshu', 'wechat']
        
        for platform in required_platforms:
            if platform not in platforms:
                print_warning(f"缺少平台配置: {platform}")
            else:
                print_success(f"平台配置存在: {platform}")
        
        return True
    except yaml.YAMLError as e:
        print_error(f"平台配置文件格式错误: {e}")
        return False
    except Exception as e:
        print_error(f"读取平台配置文件失败: {e}")
        return False

def check_python_dependencies():
    """检查Python依赖"""
    print_info("检查Python依赖...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic_settings',
        'yaml',
        'sqlalchemy',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'pydantic_settings':
                __import__('pydantic_settings')
            else:
                __import__(package)
            print_success(f"{package} 已安装")
        except ImportError:
            print_error(f"{package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"缺少以下依赖包: {', '.join(missing_packages)}")
        print_info("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_app_structure():
    """检查应用目录结构"""
    print_info("检查应用目录结构...")
    
    required_dirs = [
        Path("app"),
        Path("app/api"),
        Path("app/api/v1"),
        Path("app/services"),
        Path("app/services/formatters"),
        Path("app/config"),
        Path("app/core"),
        Path("app/schemas"),
    ]
    
    required_files = [
        Path("app/main.py"),
        Path("app/api/v1/adapter.py"),
        Path("app/services/adapter_service.py"),
        Path("app/config/platform_config.py"),
        Path("app/core/config.py"),
        Path("app/schemas/adapter.py"),
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print_success(f"目录存在: {dir_path}")
        else:
            print_error(f"目录不存在: {dir_path}")
            all_ok = False
    
    for file_path in required_files:
        if file_path.exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件不存在: {file_path}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}内容创作AI-Agent 配置检查{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    results = []
    
    # 检查应用结构
    results.append(("应用目录结构", check_app_structure()))
    
    # 检查Python依赖
    results.append(("Python依赖", check_python_dependencies()))
    
    # 检查平台配置
    results.append(("平台配置文件", check_platform_config()))
    
    # 检查.env文件
    results.append((".env文件", check_env_file()))
    
    # 总结
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}检查结果总结{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    all_passed = True
    for name, result in results:
        if result:
            print_success(f"{name}: 通过")
        else:
            print_warning(f"{name}: 警告（将使用默认配置）")
            # 平台配置和.env文件缺失不算失败，因为有默认值
    
    print(f"\n{Colors.BLUE}提示:{Colors.END}")
    print("1. 如果.env文件不存在，服务将使用默认配置")
    print("2. 如果平台配置文件不存在，将使用内置默认配置")
    print("3. 平台适配模块可以独立运行，不依赖数据库")
    print("4. 启动服务: uvicorn app.main:app --reload --port 8000")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
