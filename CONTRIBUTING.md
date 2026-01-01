# Contributing to Guardian

Thank you for your interest in contributing to Guardian! We want to make it as easy as possible to contribute to this project.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Create a feature branch** for your changes.
3. **Commit your changes** with clear, descriptive commit messages.
4. **Submit a Pull Request** (PR) clearly describing the problem and your solution.

## Development Setup

We use `poetry` for dependency management.

```bash
# Install dependencies
make install

# Run the operator locally
poetry run kopf run src/guardian/handlers.py --verbose
```

## Project Structure

- `src/guardian/`: Core logic and engines.
- `deploy/`: Kubernetes manifests (CRDs, RBAC, Deployment).
- `tests/`: Unit and integration tests.

## Running Tests

Please ensure all tests pass before submitting a PR.

```bash
# Run unit tests
make test

# Run linter
make lint
```

## Code Style

We follow PEP8 and use `black` and `isort` for formatting. Run `make format` to automatically format your code.
