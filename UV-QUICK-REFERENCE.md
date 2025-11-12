<!--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# UV Quick Reference Card

**Project:** http-api-tool-docker
**Migration Date:** November 3, 2025

---

## Installation

```bash
# Install UV (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

---

## Common Commands

### Development Setup

```bash
# Install all dependencies (dev + test)
uv sync --frozen

# Install production dependencies
uv sync --frozen --no-dev

# Install with test dependencies
uv sync --frozen --group test
```

### Running Commands

```bash
# Run any Python command
uv run python -m http_api_tool --help

# Run pytest
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=http_api_tool --cov-report=html

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Dependency Management

```bash
# Update lock file (after changing pyproject.toml)
uv lock

# Upgrade all dependencies
uv lock --upgrade

# Upgrade specific package
# (Edit pyproject.toml first, then)
uv lock

# Show installed packages
uv pip list
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=http_api_tool --cov-report=html --cov-report=term

# Run linting
uv run pre-commit run --all-files

# Format code
uv run pre-commit run --all-files ruff-format

# Run integration tests locally
./scripts/test-pypi-integration-local.sh

# Run integration tests against PyPI
./scripts/test-pypi-integration.sh
```

---

## Docker Commands

```bash
# Build image
docker build -t http-api-tool .

# Run container
docker run --rm http-api-tool test \
  --url https://example.com/api \
  --expected-http-code 200

# Build image with caching
DOCKER_BUILDKIT=1 docker build --cache-from http-api-tool:latest \
  -t http-api-tool .
```

---

## Migration from PDM

### Command Mapping

| PDM Command | UV Command |
|-------------|------------|
| `pdm install` | `uv sync --frozen --no-dev` |
| `pdm install --dev` | `uv sync --frozen` |
| `pdm install -G test` | `uv sync --frozen --group test` |
| `pdm run <cmd>` | `uv run <cmd>` |
| `pdm add <pkg>` | Edit `pyproject.toml` + `uv lock` |
| `pdm update` | `uv lock --upgrade` |
| `pdm list` | `uv pip list` |

### First-Time Migration

```bash
# 1. Remove old artifacts
rm -rf .venv .pdm-python pdm.lock

# 2. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync --frozen

# 4. Verify everything works
uv run pytest tests/ -v
```

---

## Troubleshooting

### "uv: command not found"

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"
```

### "Lock file is out of date"

```bash
# Regenerate lock file
uv lock
```

### "Module not found" errors

```bash
# Clean and reinstall
rm -rf .venv
uv sync --frozen
```

### Docker build fails

```bash
# Ensure uv.lock is in version control
git add uv.lock
git commit -m "Update uv.lock"

# Rebuild
docker build -t http-api-tool .
```

---

## File Locations

- **Lock file:** `uv.lock` (committed to git)
- **Virtual environment:** `.venv/` (gitignored)
- **Cache:** `~/.cache/uv/` (local)
- **Config:** `pyproject.toml`

---

## Key Differences from PDM

| Feature | PDM | UV |
|---------|-----|-----|
| Speed | Moderate | 10-100x faster |
| Lock file | `pdm.lock` (586 KB) | `uv.lock` (145 KB) |
| Cache location | `~/.cache/pdm` | `~/.cache/uv` |
| Run commands | `pdm run` | `uv run` |
| Add packages | `pdm add` | Edit toml + `uv lock` |
| Build backend | `pdm-backend` | `hatchling` |

---

## Resources

- **UV Docs:** <https://github.com/astral-sh/uv>
- **Migration Guide:** `MIGRATION-UV.md`
- **Full Summary:** `MIGRATION-SUMMARY.md`
- **Hatchling:** <https://hatch.pypa.io/latest/>

---

## Support

Questions? Check:

1. This reference card
2. `MIGRATION-UV.md` for details
3. `MIGRATION-SUMMARY.md` for complete overview
4. Open an issue in the repository

---

**Last Updated:** November 3, 2025
**Version:** 1.0.0
