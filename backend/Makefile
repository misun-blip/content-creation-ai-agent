# Makefile for backend testing and development

.PHONY: help install test test-verbose test-coverage test-unit test-integration test-api lint format clean run

# Default target
help:
	@echo "可用命令:"
	@echo "  install      - 安装依赖"
	@echo "  test         - 运行测试"
	@echo "  test-verbose - 运行详细测试"
	@echo "  test-coverage- 运行测试并生成覆盖率报告"
	@echo "  test-unit    - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-api     - 运行API测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  run          - 运行应用"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with verbose output
test-verbose:
	python -m pytest tests/ -v -s

# Run tests with coverage
test-coverage:
	python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Run unit tests only
test-unit:
	python -m pytest tests/ -m unit -v

# Run integration tests only
test-integration:
	python -m pytest tests/ -m integration -v

# Run API tests only
test-api:
	python -m pytest tests/ -m api -v

# Run specific test file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "请指定测试文件: make test-file FILE=test_adapter.py"; \
	else \
		python -m pytest tests/$(FILE) -v; \
	fi

# Run specific test function
test-func:
	@if [ -z "$(FUNC)" ]; then \
		echo "请指定测试函数: make test-func FUNC=test_adapt_content_douyin"; \
	else \
		python -m pytest tests/ -k $(FUNC) -v; \
	fi

# Code linting
lint:
	@echo "运行代码检查..."
	@echo "注意: 需要安装flake8和black"
	# flake8 app/ tests/
	# black --check app/ tests/

# Code formatting
format:
	@echo "格式化代码..."
	@echo "注意: 需要安装black和isort"
	# black app/ tests/
	# isort app/ tests/

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

# Run the application
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests using the custom script
test-script:
	python run_tests.py

# Run tests with coverage using the custom script
test-script-coverage:
	python run_tests.py --coverage

# Run unit tests using the custom script
test-script-unit:
	python run_tests.py --unit

# Run integration tests using the custom script
test-script-integration:
	python run_tests.py --integration

# Run API tests using the custom script
test-script-api:
	python run_tests.py --api