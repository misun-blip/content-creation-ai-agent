# 后端依赖管理说明

## 依赖文件说明

本项目将Python依赖分为三个文件，以便更好地管理不同环境的依赖：

### 1. requirements.txt - 生产环境依赖
包含运行生产环境所需的核心依赖。

**安装命令：**
```bash
pip install -r requirements.txt
```

**包含的依赖：**
- Web框架：fastapi, uvicorn
- 数据库：sqlalchemy, pymysql, alembic
- 安全认证：cryptography, python-jose, passlib
- 配置管理：pydantic, pydantic-settings, python-dotenv, PyYAML
- 缓存：redis
- AI服务：openai
- 测试：pytest, pytest-asyncio, pytest-cov, httpx

### 2. requirements-dev.txt - 开发环境依赖
包含开发过程中使用的工具，如代码格式化、静态检查、调试工具等。

**安装命令：**
```bash
pip install -r requirements-dev.txt
```

**包含的依赖：**
- 代码质量工具：flake8, black, isort, mypy, pylint
- 调试工具：ipdb, pdbpp
- 文档生成：sphinx, sphinx-rtd-theme
- 性能分析：py-spy, memory-profiler
- 安全检查：pip-audit, bandit
- 其他开发工具：watchdog

### 3. requirements-test.txt - 测试环境依赖
包含运行测试所需的工具和框架。

**安装命令：**
```bash
pip install -r requirements-test.txt
```

**包含的依赖：**
- 测试框架：pytest, pytest-asyncio, pytest-cov, pytest-mock, pytest-xdist
- HTTP测试工具：httpx, requests
- 测试工具：faker, factory-boy, freezegun, responses
- 覆盖率报告：coverage
- 性能测试：locust, pytest-benchmark

## 安装说明

### 生产环境
```bash
# 仅安装生产环境依赖
pip install -r requirements.txt
```

### 开发环境
```bash
# 安装生产环境依赖 + 开发环境依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 测试环境
```bash
# 安装生产环境依赖 + 测试环境依赖
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 完整开发环境（推荐）
```bash
# 安装所有依赖（生产 + 开发 + 测试）
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
```

## 虚拟环境建议

### 使用venv
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
```

### 使用conda
```bash
# 创建虚拟环境
conda create -n content-ai-agent python=3.10

# 激活虚拟环境
conda activate content-ai-agent

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
```

## 依赖管理最佳实践

### 1. 定期更新依赖
```bash
# 检查过期的依赖
pip list --outdated

# 更新单个依赖
pip install --upgrade package-name

# 更新所有依赖（谨慎使用）
pip-review --auto
```

### 2. 安全检查
```bash
# 检查依赖安全漏洞
pip-audit

# 使用bandit扫描代码安全问题
bandit -r app/
```

### 3. 代码质量检查
```bash
# 使用flake8检查代码风格
flake8 app/

# 使用black格式化代码
black app/

# 使用isort排序import语句
isort app/

# 使用mypy进行类型检查
mypy app/
```

### 4. 测试覆盖率
```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html tests/

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

### 5. 导出当前环境
```bash
# 导出当前安装的所有包
pip freeze > requirements-all.txt

# 仅导出项目依赖（不包含子依赖）
pipreqs --force .
```

## 常见问题

### Q: 为什么将依赖分为多个文件？
A: 分离依赖有以下好处：
1. 生产环境只安装必要的依赖，减小镜像大小
2. 开发环境可以安装额外的工具，提高开发效率
3. 测试环境可以安装专门的测试工具
4. 便于CI/CD流程管理

### Q: 如何选择要安装的依赖文件？
A: 根据使用场景选择：
- 部署到生产环境：仅 requirements.txt
- 本地开发：requirements.txt + requirements-dev.txt
- 运行测试：requirements.txt + requirements-test.txt
- 完整开发：全部三个文件

### Q: PyYAML依赖的作用是什么？
A: PyYAML用于解析YAML格式的配置文件。本项目中的平台配置文件 `platform_config.yaml` 需要使用PyYAML来加载。

### Q: 如何解决依赖冲突？
A: 如果遇到依赖冲突，可以尝试以下方法：
1. 使用 `pipdeptree` 查看依赖树：`pip install pipdeptree && pipdeptree`
2. 升级或降级冲突的包
3. 使用虚拟环境隔离不同项目的依赖

## 版本锁定说明

- **固定版本**（如 `==1.0.0`）：用于关键依赖，确保稳定性
- **最低版本**（如 `>=1.0.0`）：用于兼容性要求不严格的依赖
- **建议使用固定版本**：在生产环境中，建议使用固定版本以避免意外更新导致的问题

## 相关文档

- [平台适配模块依赖检查报告](../docs/平台适配模块依赖检查报告.md)
- [开发流程文档](../文档集合/开发流程文档.md)
- [API接口文档](../docs/API.md)

## 联系方式

如有依赖相关问题，请联系开发团队。
