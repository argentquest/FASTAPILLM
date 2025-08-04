# Contributing to FASTAPILLM

We love your input! We want to make contributing to FASTAPILLM as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. **Fork the repo** and create your branch from `main`.
2. **Add tests** if you've added code that should be tested.
3. **Update documentation** if you've changed APIs or added features.
4. **Ensure the test suite passes** by running `pytest`.
5. **Make sure your code follows our style** by running `black .` and `isort .`.
6. **Write a clear commit message** describing your changes.
7. **Issue the pull request** with a comprehensive description.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- An AI provider API key (Azure OpenAI, OpenRouter, or custom)

### Local Development

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/FASTAPILLM.git
   cd FASTAPILLM
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your test configuration
   ```

6. **Initialize the database**:
   ```bash
   python -c "from database import init_db; init_db()"
   ```

7. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

8. **Start the development server**:
   ```bash
   uvicorn main:app --reload
   ```

## Code Style

We use several tools to maintain code quality:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting

```bash
black .
isort .
```

### Linting
- **flake8**: Style guide enforcement
- **mypy**: Type checking

```bash
flake8 .
mypy .
```

### Pre-commit Hooks

We recommend using pre-commit hooks to automatically format and check your code:

```bash
pip install pre-commit
pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test files
pytest tests/test_services.py
pytest tests/test_routes.py

# Run tests with specific markers
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
```

### Writing Tests

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test interactions between components
- **API tests**: Test API endpoints end-to-end

Test files should be placed in the `tests/` directory and follow the naming convention `test_*.py`.

Example test structure:
```python
import pytest
from services.base_service import BaseService

class TestBaseService:
    def test_initialization(self):
        """Test service initialization"""
        service = BaseService()
        assert service.provider == "azure"  # or configured provider
    
    @pytest.mark.asyncio
    async def test_api_call(self):
        """Test API call functionality"""
        # Test implementation
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions, classes, and modules should have comprehensive docstrings
- **Type hints**: Use type hints for all function parameters and return values
- **Comments**: Add comments for complex logic or business rules

### Documentation Updates

When making changes that affect the API or user experience:

1. **Update README.md** with new features or configuration changes
2. **Update ARCHITECTURE.md** for architectural changes
3. **Add examples** to demonstrate new functionality
4. **Update API documentation** if endpoints change

## Reporting Bugs

We use GitHub issues to track public bugs. Report a bug by opening a new issue.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure the application with '...'
2. Make API call to '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
- OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g. 3.11.0]
- Application version: [e.g. 1.0.0]
- AI Provider: [e.g. Azure OpenAI, OpenRouter]

**Additional context**
Add any other context about the problem here, including:
- Configuration (sanitized, no API keys)
- Log output (relevant portions)
- Screenshots if applicable
```

## Feature Requests

We welcome feature requests! Please open a GitHub issue with the "enhancement" label.

**Great Feature Requests** include:

- **Clear description** of the feature and its benefits
- **Use cases** showing how the feature would be used
- **Implementation suggestions** if you have ideas
- **Compatibility considerations** with existing features

### Feature Request Template

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Use cases**
Describe specific use cases where this feature would be beneficial.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Adding New AI Frameworks

To add support for a new AI framework:

1. **Create service classes**:
   ```python
   # services/content_services/new_framework_service.py
   from ..base_service import BaseService
   
   class NewFrameworkService(BaseService):
       async def generate_content(self, primary_input: str, secondary_input: str):
           # Implementation
   ```

2. **Create chat service**:
   ```python
   # services/chat_services/new_framework_chat_service.py
   from .base_chat_service import ChatService
   
   class NewFrameworkChatService(ChatService):
       # Implementation
   ```

3. **Add prompt files**:
   ```
   prompts/new_framework/
   ├── system_prompt.txt
   ├── chat_system_prompt.txt
   └── user_template.txt
   ```

4. **Update prompt loading**:
   ```python
   # prompts/chat_prompts.py
   def get_new_framework_chat_prompt() -> str:
       # Implementation
   ```

5. **Add API routes**:
   ```python
   # routes/story_routes.py
   @router.post("/new-framework")
   async def generate_with_new_framework(request: ContentRequest):
       # Implementation
   ```

6. **Add comprehensive tests**
7. **Update documentation**

## Adding New AI Providers

To add support for a new AI provider:

1. **Extend client creation** in `BaseService._create_client()`
2. **Add configuration options** in `config.py`
3. **Update error handling** for provider-specific errors
4. **Add provider-specific tests**
5. **Update configuration documentation**

## Release Process

1. **Version bumping**: Update version in `__init__.py` and relevant files
2. **Changelog**: Update `CHANGELOG.md` with new features, fixes, and breaking changes
3. **Documentation**: Ensure all documentation is up to date
4. **Testing**: Run full test suite including integration tests
5. **Tagging**: Create a git tag with the new version
6. **Release notes**: Create comprehensive release notes on GitHub

## Community

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Email**: For security issues or private inquiries

### Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Be mindful** of your language and actions
- **Be patient** with newcomers and different skill levels

## Recognition

Contributors will be recognized in:
- **Contributors section** of the README
- **Changelog** for significant contributions
- **Release notes** for major features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask questions by opening an issue or reaching out through GitHub Discussions. We're here to help!