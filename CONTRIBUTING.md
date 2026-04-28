# Contributing to RV1126B Test Tool

Thank you for your interest in contributing to the RV1126B Test Tool! We welcome all forms of contribution, from bug reports and feature requests to code contributions and documentation improvements.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- ADB (Android Debug Bridge)
- RV1126B/RK3576 development board (for testing)

### Quick Setup

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/RV1126B_Test_Tool.git
   cd RV1126B_Test_Tool
   ```
3. **Create** a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run** the application:
   ```bash
   python main.py
   ```

## 🛠️ Development Setup

### IDE Recommendations

- **VS Code** with Python extension
- **PyCharm Professional** (recommended for Qt development)
- Any editor with Python support

### Required Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-vscode.vscode-json"
  ]
}
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

## 🤝 How to Contribute

### Types of Contributions

1. **🐛 Bug Reports**: Report bugs via GitHub Issues
2. **✨ Feature Requests**: Suggest new features
3. **📝 Documentation**: Improve documentation
4. **💻 Code Contributions**: Fix bugs or add features
5. **🧪 Testing**: Write or improve tests
6. **🌐 Translation**: Help with internationalization

### Contribution Workflow

1. **Choose an issue** or create your own
2. **Create a branch** for your work
3. **Make your changes** following our guidelines
4. **Write tests** if applicable
5. **Update documentation** if needed
6. **Submit a pull request**

## 📏 Development Guidelines

### Code Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters
- **Quotes**: Use double quotes for strings
- **Imports**: Organize with isort
- **Formatting**: Use Black formatter

### Naming Conventions

```python
# Classes
class TestCaseManager:
    pass

# Functions and methods
def validate_test_case():
    pass

# Variables
test_case_list = []
device_serial = "abc123"

# Constants
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
```

### Documentation

- Use docstrings for all public functions/classes
- Follow Google style docstrings
- Include type hints where possible

```python
def validate_device_connection(device_serial: str) -> bool:
    """Validate ADB connection to target device.

    Args:
        device_serial: Device serial number

    Returns:
        True if connection is valid, False otherwise

    Raises:
        ADBError: If ADB command fails
    """
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_specific.py

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Writing Tests

- Use `pytest` framework
- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names

```python
def test_device_connection_success():
    """Test successful device connection."""
    # Arrange
    device_serial = "test_device"

    # Act
    result = connect_device(device_serial)

    # Assert
    assert result is True
```

### Test Coverage

Aim for >80% code coverage. Critical components should have >90% coverage.

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure** your code follows our guidelines
2. **Update** documentation if needed
3. **Add tests** for new functionality
4. **Ensure** all tests pass
5. **Update** CHANGELOG.md if applicable

### PR Template

Please use our PR template and fill in all relevant sections:

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(test): add automated recording mark test
fix(ui): resolve table widget scaling issue
docs(readme): update installation instructions
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of the issue
- **Steps to reproduce**:
  1. Step 1
  2. Step 2
  3. Step 3
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, hardware
- **Logs**: Relevant log output
- **Screenshots**: If applicable

### Feature Requests

For feature requests, please include:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of the feature
- **Use case**: Why this feature would be useful
- **Proposed solution**: How you think it should work
- **Alternatives**: Other solutions you've considered

## 📚 Additional Resources

- [Architecture Overview](./doc/上位机项目架构.mk)
- [API Reference](./doc/api_reference.md)
- [Development Guide](./doc/development/getting_started.md)
- [Testing Guide](./doc/development/testing_guide.md)

## 🙏 Recognition

Contributors will be recognized in our CHANGELOG.md and potentially in future release notes. We appreciate all contributions, big and small!

---

Thank you for contributing to RV1126B Test Tool! 🚀