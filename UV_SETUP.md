# UV Setup Guide for FASTAPILLM

This project **uses UV as the primary package manager**. UV is a fast Python package manager written in Rust that replaces pip with significant performance improvements.

## 🎉 Project Status: UV Migration Complete!

This project has been successfully migrated to UV and is now fully optimized for faster development workflows.

## Installation

### Windows
```powershell
# PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Alternative: Install with pip
```bash
pip install uv
```

## Project Setup with UV

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd langchainone
```

### 2. Create Virtual Environment
```bash
# UV will automatically use Python 3.11 from .python-version file
uv venv

# Activate the virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install project with all extras (recommended)
uv pip install -e ".[dev,test]"

# Alternative: Install specific extras
uv pip install -e ".[dev]"     # Development dependencies
uv pip install -e ".[test]"    # Test dependencies

# Basic installation only
uv pip install -e .
```

### 4. Create UV Lock File (First Time)
```bash
# Generate uv.lock from pyproject.toml
uv lock
```

### 5. Install from Lock File (Reproducible Installs)
```bash
# Install exact versions from lock file
uv pip sync uv.lock
```

## Common UV Commands

### Package Management
```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package fastapi
```

### Virtual Environment
```bash
# Create new virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.12

# Remove virtual environment
rm -rf .venv  # or manually delete .venv folder on Windows
```

### Running Commands
```bash
# Run Python scripts
uv run python backend/main.py

# Run pytest
uv run pytest

# Run with specific Python version
uv run --python 3.11 python script.py
```

### Installing Tools
```bash
# Install development tools globally
uv tool install black
uv tool install ruff
uv tool install mypy

# Run tools
uv tool run black .
uv tool run ruff check
```

## Development Workflow

### Initial Setup (One Time)
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# OR
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone project
git clone <repository-url>
cd langchainone

# Create virtual environment and install all dependencies
uv venv --python 3.11
source .venv/Scripts/activate  # Windows
# OR
source .venv/bin/activate  # macOS/Linux

# Install project with all dependencies (164 packages)
uv pip install -e ".[dev,test]"

# Generate lock file for reproducible builds
uv lock
```

### Daily Development
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Sync dependencies (in case they changed)
uv pip sync uv.lock

# Run the application
python backend/main.py

# Run tests
pytest
```

### Adding New Dependencies
```bash
# Add to pyproject.toml and update lock file
uv add fastapi

# Add dev dependency
uv add --dev pytest-mock

# Sync your environment
uv pip sync uv.lock
```

## Migration from pip/requirements.txt

If you're migrating from pip:

1. **Existing virtual environment**: Delete it and create new with UV
   ```bash
   rm -rf venv  # or your venv folder name
   uv venv
   ```

2. **Install from pyproject.toml instead of requirements.txt**
   ```bash
   # Old way
   pip install -r requirements.txt
   
   # New way
   uv pip sync pyproject.toml
   ```

3. **Lock file for reproducible installs**
   ```bash
   # Generate lock file
   uv lock
   
   # Commit both pyproject.toml and uv.lock to git
   git add pyproject.toml uv.lock
   git commit -m "Add UV configuration"
   ```

## Benefits of UV

1. **Speed**: 10-100x faster than pip
2. **Reproducible**: Lock files ensure exact same versions
3. **Simple**: Drop-in replacement for pip commands
4. **Reliable**: Written in Rust, handles edge cases better
5. **Modern**: Built-in support for PEP standards

## Troubleshooting

### UV command not found
- Make sure UV is in your PATH after installation
- Restart your terminal after installation
- On Windows, you may need to add `%USERPROFILE%\.cargo\bin` to PATH

### Python version issues
- UV respects `.python-version` file (set to 3.11)
- Install Python 3.11 if not available
- Use `uv venv --python 3.11` to explicitly set version

### Package conflicts
- Delete `uv.lock` and regenerate: `uv lock`
- Clear UV cache: `uv cache clean`
- Check for conflicting version requirements in pyproject.toml

## CI/CD Integration

### GitHub Actions
```yaml
- name: Install UV
  uses: astral-sh/setup-uv@v3
  
- name: Create venv and install dependencies
  run: |
    uv venv
    uv pip sync uv.lock
    
- name: Run tests
  run: |
    uv run pytest
```

### Docker
```dockerfile
# Install UV in Docker
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv venv && uv pip sync uv.lock
```

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV Command Reference](https://github.com/astral-sh/uv#commands)
- [Migration Guide](https://github.com/astral-sh/uv#migrating-from-pip)