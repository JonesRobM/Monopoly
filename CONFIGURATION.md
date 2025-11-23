# Configuration Files Guide

This document explains all configuration files in the project and their purposes.

## Table of Contents

- [Python Packaging](#python-packaging)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Editor Configuration](#editor-configuration)
- [Version Control](#version-control)
- [CI/CD](#cicd)
- [Documentation](#documentation)

## Python Packaging

### `pyproject.toml`
Modern Python packaging configuration (PEP 518/621).

**Purpose**: Centralizes all project metadata and tool configurations.

**Key Sections**:
- `[project]`: Package metadata, dependencies
- `[project.optional-dependencies]`: Extra dependency groups (dev, rl, analysis)
- `[tool.black]`: Black formatter settings
- `[tool.ruff]`: Ruff linter configuration
- `[tool.mypy]`: MyPy type checker settings
- `[tool.pytest.ini_options]`: Pytest configuration
- `[tool.coverage]`: Coverage reporting settings

**Usage**:
```bash
# Install package
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with all extras
pip install -e ".[all]"
```

### `setup.py`
Legacy setup script (still used by some tools).

**Purpose**: Provides backward compatibility for tools that don't support `pyproject.toml`.

**Status**: Will be deprecated once all tools support `pyproject.toml`.

### `requirements.txt`
Minimal runtime dependencies.

**Purpose**: Provides a simple way to install core dependencies without setuptools.

**Usage**:
```bash
pip install -r requirements.txt
```

**Contents**:
- numpy
- pettingzoo
- gymnasium

### `MANIFEST.in`
Source distribution file inclusion rules.

**Purpose**: Specifies which non-Python files to include in source distributions.

**Includes**:
- Documentation files (README, LICENSE, etc.)
- Configuration files
- Type checking markers (py.typed)

## Code Quality

### `.flake8`
Flake8 linter configuration.

**Purpose**: Python code style checking (PEP 8 compliance).

**Settings**:
- Line length: 100
- McCabe complexity: 10
- Excluded directories: `.git`, `__pycache__`, etc.

**Usage**:
```bash
flake8 engine env
```

**Note**: Consider using `ruff` instead (configured in `pyproject.toml`).

### `pyproject.toml` - `[tool.ruff]`
Ruff linter configuration (faster alternative to flake8).

**Purpose**: Fast Python linting with auto-fix capabilities.

**Enabled Rules**:
- E/W: pycodestyle errors and warnings
- F: pyflakes
- I: isort (import sorting)
- B: flake8-bugbear
- C4: flake8-comprehensions
- UP: pyupgrade

**Usage**:
```bash
# Check code
ruff check engine env

# Auto-fix issues
ruff check --fix engine env
```

### `pyproject.toml` - `[tool.black]`
Black code formatter configuration.

**Purpose**: Automatic code formatting for consistency.

**Settings**:
- Line length: 100
- Target version: Python 3.12

**Usage**:
```bash
# Format code
black engine env

# Check formatting
black --check engine env
```

### `pyproject.toml` - `[tool.mypy]`
MyPy static type checker configuration.

**Purpose**: Static type checking to catch type errors before runtime.

**Settings**:
- Strict mode enabled
- Disallow untyped definitions
- Warn on redundant casts
- Ignore missing imports (for third-party packages)

**Usage**:
```bash
mypy engine env
```

### `.pre-commit-config.yaml`
Pre-commit hooks configuration.

**Purpose**: Automatically run checks before each commit.

**Hooks**:
- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML validation
- Black formatting
- Ruff linting
- MyPy type checking
- Pytest tests

**Setup**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Testing

### `pytest.ini`
Pytest configuration (also in `pyproject.toml`).

**Purpose**: Configure test discovery and execution.

**Settings**:
- Test paths: `engine/tests`
- Verbose output
- Short traceback
- Test markers (unit, integration, slow)

**Usage**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=engine --cov=env

# Run specific markers
pytest -m "not slow"
pytest -m integration
```

### `pyproject.toml` - `[tool.coverage]`
Coverage.py configuration.

**Purpose**: Measure and report test coverage.

**Settings**:
- Source: `engine`, `env`
- Omit: tests, `__pycache__`
- HTML output: `htmlcov/`

**Usage**:
```bash
# Generate coverage report
pytest --cov=engine --cov=env --cov-report=html

# View report
open htmlcov/index.html
```

## Editor Configuration

### `.editorconfig`
Cross-editor configuration file.

**Purpose**: Ensure consistent coding styles across different editors and IDEs.

**Settings**:
- Charset: UTF-8
- End of line: LF
- Indentation: 4 spaces for Python, 2 for YAML/JSON
- Trim trailing whitespace

**Supported Editors**:
- VS Code (with EditorConfig extension)
- PyCharm (built-in support)
- Sublime Text (with EditorConfig package)
- Vim/Neovim (with editorconfig plugin)

## Version Control

### `.gitignore`
Git ignore patterns.

**Purpose**: Exclude generated files from version control.

**Excluded**:
- Python bytecode (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `.venv/`)
- Build artifacts (`build/`, `dist/`, `*.egg-info`)
- IDE files (`.vscode/`, `.idea/`)
- Test/coverage artifacts (`.pytest_cache/`, `htmlcov/`)

## CI/CD

### `.github/workflows/ci.yml`
GitHub Actions CI/CD workflow.

**Purpose**: Automated testing, linting, and building on GitHub.

**Jobs**:
1. **test**: Run tests on multiple OS/Python versions
   - Ubuntu, Windows, macOS
   - Python 3.12, 3.13
   - Upload coverage to Codecov

2. **lint**: Code quality checks
   - Ruff linting
   - Black formatting check
   - MyPy type checking

3. **build**: Package building
   - Build source and wheel distributions
   - Validate with twine

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main`

## Build Tools

### `Makefile`
Common development tasks.

**Purpose**: Simplify common commands with short aliases.

**Targets**:
- `make install`: Install package
- `make install-dev`: Install with dev dependencies
- `make test`: Run tests
- `make test-cov`: Run tests with coverage
- `make lint`: Run all linters
- `make format`: Format code
- `make clean`: Clean build artifacts
- `make example`: Run example script

**Usage**:
```bash
make help  # Show all targets
```

**Windows Users**: Use the `-windows` variants for some targets:
```bash
make clean-windows
```

## Type Checking

### `engine/py.typed` and `env/py.typed`
PEP 561 type marker files.

**Purpose**: Indicate that packages support type checking.

**Effect**:
- Tells MyPy the packages are typed
- Allows other projects to type-check against your code
- Required for distributing typed packages

## License Files

### `LICENSE`
Apache License 2.0 full text.

**Purpose**: Defines the terms under which the software is distributed.

**Type**: Apache License 2.0

**Key Points**:
- Permissive open source license
- Allows commercial use, modification, distribution
- Requires preservation of copyright and license notices
- Provides patent grant from contributors
- Includes disclaimer of warranty

### `NOTICE`
Apache NOTICE file (required by Apache License 2.0).

**Purpose**: Contains copyright notices and attributions.

**Contents**:
- Project copyright notice
- Third-party library attributions
- Trademark disclaimer for "Monopoly"

**Note**: Must be included in distributions per Apache License 2.0 requirements.

### `.license-header.txt`
Standard license header template for source files.

**Purpose**: Template for adding license headers to Python files.

**Usage**: Optional but recommended for all new source files.

## Documentation

### `README.md`
Main project documentation.

**Contents**:
- Project overview and status
- Installation instructions
- Usage examples
- Architecture overview
- Development roadmap

### `CLAUDE.md`
Project design and architectural guidelines.

**Contents**:
- Project goals and scope
- Architectural principles
- Directory layout
- Agent types and training protocol
- Coding standards

### `CONTRIBUTING.md`
Contribution guidelines.

**Contents**:
- Development setup
- Coding standards
- Testing requirements
- Pull request process

### `CHANGELOG.md`
Version history and changes.

**Format**: Keep a Changelog format

**Contents**:
- Unreleased changes
- Version releases with dates
- Categorized changes (Added, Changed, Fixed, etc.)

### `IMPLEMENTATION_SUMMARY.md`
Phase 1 completion summary.

**Contents**:
- What was built
- Test results
- File structure
- Next steps

## Configuration Best Practices

### 1. Single Source of Truth
Use `pyproject.toml` as the primary configuration source when possible.

### 2. Tool Compatibility
Some tools still require separate config files (`.flake8`, `pytest.ini`). These will be migrated to `pyproject.toml` as tool support improves.

### 3. Version Control
- **Include**: All configuration files
- **Exclude**: Generated files, caches, build artifacts

### 4. Overrides
Local overrides (for development) should go in files that are `.gitignore`'d:
- `.env` for environment variables
- `local_settings.py` (if needed)

### 5. Documentation
Keep this file updated when adding new configurations.

## Quick Reference

| Task | Command |
|------|---------|
| Install package | `pip install -e .` |
| Install dev deps | `pip install -e ".[dev]"` |
| Run tests | `pytest` or `make test` |
| Format code | `black engine env` or `make format` |
| Lint code | `ruff check engine env` or `make lint` |
| Type check | `mypy engine env` or `make type-check` |
| Coverage report | `pytest --cov=engine --cov=env --cov-report=html` |
| Clean artifacts | `make clean` |
| Run example | `python example_usage.py` |

## Troubleshooting

### Issue: Pre-commit hooks fail
**Solution**: Run manually and fix issues:
```bash
pre-commit run --all-files
make format
make lint
```

### Issue: Type checking errors
**Solution**: Add type stubs or ignore imports:
```python
# In code
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import some_untyped_package

# Or in pyproject.toml [tool.mypy]
[[tool.mypy.overrides]]
module = "untyped_package.*"
ignore_missing_imports = true
```

### Issue: Coverage too low
**Solution**: Add more tests or adjust coverage threshold in `pyproject.toml`.

### Issue: Makefile doesn't work on Windows
**Solution**: Use `-windows` variants or run commands directly:
```bash
make clean-windows
# or
pytest
black engine env
```

## Further Reading

- [PEP 518](https://peps.python.org/pep-0518/): pyproject.toml
- [PEP 621](https://peps.python.org/pep-0621/): Project metadata
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
