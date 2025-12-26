# Contributing to AI Risk Sentinel

Thank you for your interest in contributing to AI Risk Sentinel! This document provides guidelines and instructions for contributing to the project.

## 🌟 Ways to Contribute

- **Report Bugs**: Open an issue describing the bug
- **Suggest Features**: Open an issue with your feature proposal
- **Submit Pull Requests**: Fix bugs or implement features
- **Improve Documentation**: Fix typos, clarify explanations, add examples
- **Add Tests**: Increase test coverage
- **Review PRs**: Help review other contributors' pull requests

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Development Setup

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/AI-Risk-Sentinel.git
cd AI-Risk-Sentinel

# Add upstream remote
git remote add upstream https://github.com/Preventera/AI-Risk-Sentinel.git

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Start services
docker-compose up -d db redis
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ai_risk_sentinel

# Run specific test file
pytest tests/test_core.py -v

# Run tests matching a pattern
pytest -k "test_bsi" -v
```

## 📝 Development Workflow

### 1. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, well-documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Commit Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

# Examples:
git commit -m "feat(gap-detector): add temporal analysis support"
git commit -m "fix(api): handle missing model cards gracefully"
git commit -m "docs: update installation instructions"
git commit -m "test: add tests for compliance checker"
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📋 Code Standards

### Python Style

We use the following tools:
- **Black**: Code formatting
- **isort**: Import sorting
- **ruff**: Linting
- **mypy**: Type checking

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
ruff check src/ tests/

# Type checking
mypy src/
```

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Include type hints

```python
def calculate_bsi(self, documented: float, incidents: float) -> float:
    """
    Calculate Blind Spot Index for a category.
    
    BSI = |documented% - incidents%| / max(documented%, incidents%)
    
    Args:
        documented: Percentage of documented risks in this category
        incidents: Percentage of real-world incidents in this category
        
    Returns:
        Blind Spot Index between 0 and 1
        
    Example:
        >>> detector = GapDetector()
        >>> bsi = detector.calculate_bsi(4.0, 22.4)
        >>> print(f"BSI: {bsi:.2f}")
        BSI: 0.82
    """
```

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for setup
- Test edge cases

```python
def test_calculate_bsi_complete_misalignment():
    """Test BSI calculation with complete misalignment."""
    detector = GapDetector()
    bsi = detector.calculate_bsi(documented=0.0, incidents=100.0)
    assert bsi == 1.0
```

## 🏗️ Architecture Guidelines

### AgenticX5 Levels

When adding new agents, follow the AgenticX5 architecture:

| Level | Purpose | Examples |
|-------|---------|----------|
| N1 | Collection | HF_Crawler, Incident_Monitor |
| N2 | Normalization | Classifier, Deduplicator |
| N3 | Analysis | Gap_Detector, Risk_Propagation |
| N4 | Recommendation | Checklist_Generator |
| N5 | Orchestration | RiskDoc_Filler |

### File Organization

```
src/ai_risk_sentinel/
├── agents/           # Agent implementations
│   ├── n1/          # Collection agents
│   ├── n2/          # Normalization agents
│   └── ...
├── api/             # FastAPI endpoints
├── core/            # Core business logic
├── models/          # Pydantic models
└── utils/           # Utilities
```

## 🔍 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted (`black`, `isort`)
- [ ] Linting passes (`ruff`)
- [ ] Type checking passes (`mypy`)
- [ ] Documentation is updated
- [ ] Commit messages follow convention

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other

## Related Issues
Closes #123

## Testing
Describe how you tested the changes

## Screenshots (if applicable)
```

## 🐛 Reporting Issues

### Bug Reports

Include:
1. Python version and OS
2. Steps to reproduce
3. Expected vs actual behavior
4. Error messages/stack traces
5. Minimal code example

### Feature Requests

Include:
1. Use case description
2. Proposed solution
3. Alternatives considered
4. Impact on existing features

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions help make AI systems safer for everyone. We appreciate your time and effort!

---

**Questions?** Open an issue or reach out to the maintainers.
