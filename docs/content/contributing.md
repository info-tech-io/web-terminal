---
title: "Contributing"
description: "Contributing guidelines for Web Terminal project - development setup, coding standards, and contribution process"
date: 2024-09-23
draft: false
weight: 5
---

# Contributing to Web Terminal

We welcome contributions to the Web Terminal project! This guide will help you get started with development and understand our contribution process.

## Getting Started

### Development Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/info-tech-io/web-terminal.git
   cd web-terminal
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Verify Docker setup:**
   ```bash
   docker --version
   docker ps
   ```

4. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

5. **Start development server:**
   ```bash
   python app.py
   ```

### Development Dependencies

Create `requirements-dev.txt`:
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.991
coverage>=6.0.0
pre-commit>=2.20.0
```

## Project Structure

```
web-terminal/
├── app.py                 # Main application
├── Dockerfile            # Container definition
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── templates/
│   └── index.html        # Frontend template
├── static/              # Static assets (if any)
├── tests/               # Test suite
│   ├── test_app.py      # Application tests
│   ├── test_container.py # Container management tests
│   └── test_websocket.py # WebSocket tests
├── docs/                # Documentation
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

## Development Workflow

### Code Standards

**Python Code Style:**
- Follow PEP 8 guidelines
- Use Black for automatic formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

**Example:**
```python
from typing import Optional, Dict, Any
import docker
from flask import Flask

def create_container(
    client: docker.DockerClient,
    image_name: str,
    config: Optional[Dict[str, Any]] = None
) -> docker.models.containers.Container:
    """Create a new Docker container with specified configuration.

    Args:
        client: Docker client instance
        image_name: Name of the Docker image to use
        config: Optional container configuration

    Returns:
        Created Docker container instance

    Raises:
        docker.errors.APIError: If container creation fails
    """
    default_config = {
        'detach': True,
        'tty': True,
        'stdin_open': True
    }

    if config:
        default_config.update(config)

    return client.containers.run(image_name, **default_config)
```

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install hooks:
```bash
pre-commit install
```

## Testing

### Test Structure

**Unit Tests:**
```python
# tests/test_container.py
import pytest
import docker
from unittest.mock import Mock, patch
from app import create_container, cleanup_container

class TestContainerManagement:
    @patch('docker.from_env')
    def test_create_container_success(self, mock_docker):
        """Test successful container creation."""
        mock_client = Mock()
        mock_container = Mock()
        mock_client.containers.run.return_value = mock_container
        mock_docker.return_value = mock_client

        result = create_container(mock_client, 'test-image')

        assert result == mock_container
        mock_client.containers.run.assert_called_once()

    def test_container_config_validation(self):
        """Test container configuration validation."""
        config = {
            'mem_limit': '256m',
            'cpu_shares': 512
        }

        validated_config = validate_container_config(config)

        assert validated_config['mem_limit'] == '256m'
        assert validated_config['cpu_shares'] == 512
```

**Integration Tests:**
```python
# tests/test_integration.py
import pytest
import docker
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint."""
    rv = client.get('/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] in ['healthy', 'degraded', 'unhealthy']

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection establishment."""
    # WebSocket testing implementation
    pass
```

**Running Tests:**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_container.py

# Run tests with verbose output
python -m pytest -v
```

## Feature Development

### Adding New Features

1. **Create feature branch:**
   ```bash
   git checkout -b feature/websocket-authentication
   ```

2. **Implement feature with tests:**
   ```python
   # Add feature code
   # Add corresponding tests
   # Update documentation
   ```

3. **Test thoroughly:**
   ```bash
   python -m pytest
   python app.py  # Manual testing
   ```

4. **Update documentation:**
   - Update relevant markdown files
   - Add code examples if applicable
   - Update API documentation

### Code Review Checklist

**Before submitting:**
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact considered

## Bug Fixes

### Bug Report Process

When reporting bugs, include:

1. **Environment information:**
   - Python version
   - Docker version
   - Operating system
   - Browser (if frontend issue)

2. **Steps to reproduce:**
   ```
   1. Start application with `python app.py`
   2. Open browser to localhost:8080
   3. Type command 'ls -la'
   4. Observe error in console
   ```

3. **Expected vs actual behavior**

4. **Relevant logs:**
   ```
   ERROR - Container failed to start: docker.errors.APIError
   ```

### Bug Fix Process

1. **Reproduce the bug locally**
2. **Write a failing test that demonstrates the bug**
3. **Fix the bug**
4. **Verify the test now passes**
5. **Check for regression in other areas**

## Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples for technical concepts
- Maintain consistency with existing documentation
- Test all code examples

### Documentation Types

**User Documentation:**
- Getting started guides
- Feature explanations
- Configuration options
- Troubleshooting guides

**Developer Documentation:**
- API references
- Architecture explanations
- Contributing guidelines
- Testing procedures

## Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Pre-release:**
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Version numbers updated

2. **Release:**
   - [ ] Create release branch
   - [ ] Tag release
   - [ ] Build and test release
   - [ ] Publish to PyPI (if applicable)

3. **Post-release:**
   - [ ] Update main branch
   - [ ] Create GitHub release
   - [ ] Update documentation site

## Communication

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Email**: For security issues or private inquiries

### Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the code of conduct

## Security

### Security Policy

- Report security vulnerabilities privately via email
- Do not include sensitive information in public issues
- Allow reasonable time for fixes before disclosure

### Security Best Practices

- Never commit secrets or API keys
- Validate all user inputs
- Use secure defaults
- Keep dependencies updated

## Performance Guidelines

### Performance Considerations

- Monitor memory usage with multiple concurrent sessions
- Test WebSocket connection limits
- Optimize Docker container lifecycle
- Consider caching strategies

### Benchmarking

```python
# Example performance test
import time
import concurrent.futures

def test_concurrent_sessions():
    """Test multiple concurrent WebSocket sessions."""
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(create_websocket_session)
            for _ in range(10)
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            assert result.status_code == 200

    duration = time.time() - start_time
    print(f"10 concurrent sessions completed in {duration:.2f} seconds")
```

---

*Ready to contribute? Start by checking our [open issues](https://github.com/info-tech-io/web-terminal/issues) or propose a new feature in [discussions](https://github.com/info-tech-io/web-terminal/discussions).*