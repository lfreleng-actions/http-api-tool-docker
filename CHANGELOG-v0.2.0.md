<!--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# Changelog - v0.2.0

## 🎉 Major Release: Dual Deployment Support

This release introduces a significant performance improvement by adding
**uvx deployment** as the new default method, alongside the existing Docker
deployment option.

---

## 🚀 New Features

### Dual Deployment Methods

#### 1. **uvx Deployment (New Default)**

- ⚡ **6x faster** than Docker deployment (~10s vs ~60s)
- 🎯 Direct installation from PyPI using `uvx`
- 💾 No Docker layer caching required
- 🔄 Automatic Python environment management
- **This is now the default deployment method**

#### 2. **Docker Deployment (Optional)**

- 🐳 Container-based isolation
- 🔒 Same security features as before
- 📦 Available when explicitly requested via `deploy: 'docker'`

### New Action Inputs

- **`deploy`**: Choose deployment method
  - `uvx` (default): Fast PyPI-based deployment
  - `docker`: Traditional containerized deployment

- **`python_version`**: Specify Python version when using uvx
  - Default: `3.11`
  - Supported: `3.10`, `3.11`, `3.12`, `3.13`

### Dynamic Versioning

- ✨ Full **hatch-vcs** integration
- 🏷️ Version automatically derived from Git tags
- 📦 No manual version updates required
- 🔄 Development versions include `.devN` suffix

### Enhanced CLI

- 🏷️ **Version display** with tag emoji on all help commands
- ✅ `--version` flag support: `http-api-tool --version`
- 📋 Version shown as first line in help output (both `--help` and `-h`)
- 🎯 Matches `dependamerge` CLI patterns

---

## 🔧 Technical Improvements

### Build System

- Upgraded to `hatchling>=1.24`
- Added `hatch-vcs>=0.4` for dynamic versioning
- Configured VCS-based version management
- Auto-generated `_version.py` file (gitignored)

### Configuration Changes

- `pyproject.toml`:
  - Added `hatch-vcs` to build requirements
  - Configured VCS version source
  - Set `local_scheme = "no-local-version"` for clean versions
  - Added build hook for version file generation

### Code Quality

- Removed hardcoded version string (`1.0.0`)
- Version imported from auto-generated `_version.py`
- Better separation of concerns in CLI module
- Custom `Typer` class for consistent version display

### Docker Publishing

- 🐳 **Automated Docker Image Publishing**: Images published to GHCR on every release
  - Multi-architecture support (linux/amd64, linux/arm64)
  - Tagged with semantic version (e.g., `v0.2.0`, `0.2`, `0`)
  - Tagged with `latest` for most recent release
  - Runs in parallel with PyPI publishing for faster releases
  - Comprehensive layer caching for efficient builds
  - Published to `ghcr.io/lfreleng-actions/http-api-tool-docker`

### Testing & Quality Assurance

- 🧪 **Integration Test Suite**: Comprehensive end-to-end validation
  - Automated testing of published PyPI package using `uvx`
  - Uses self-hosted `go-httpbin-action` for reliable testing (no external dependencies)
  - Validates version matches git tag
  - Tests all HTTP methods (GET, POST, PUT, DELETE)
  - Verifies JSON handling, regex matching, and retry logic
  - Tests HTTPS with SSL/TLS certificate validation
  - Runs automatically after PyPI release in CI/CD pipeline
- 🔄 **CI Integration**: Final validation job in `build-test-release.yaml`

---

## 📝 Files Changed

### Core Files

- ✏️ `action.yaml`: Converted from Docker to composite action
- ✏️ `pyproject.toml`: Added hatch-vcs configuration
- ✏️ `src/http_api_tool/__init__.py`: Import version from `_version.py`
- ✏️ `src/http_api_tool/cli.py`: Added version callback and CustomTyper
- ✏️ `.gitignore`: Added `src/http_api_tool/_version.py`

### Documentation

- ✏️ `README.md`: Added deployment methods section and comparison table
- ✨ `MIGRATION.md`: Complete migration guide for users
- ✨ `.github/workflows-examples/test-both-deployments.yaml`: Example workflows

### Testing

- ✏️ `.github/workflows/build-test-release.yaml`: Added integration-test and
  docker-publish jobs

---

## 📊 Performance Comparison

<!-- markdownlint-disable MD060 -->

| Metric                 | uvx (default) | docker      |
| ---------------------- | ------------- | ----------- |
| **Cold Start**         | ~10 seconds   | ~60 seconds |
| **Cached Run**         | ~5 seconds    | ~15 seconds |
| **Build Required**     | ❌ No          | ✅ Yes       |
| **Container Overhead** | ❌ None        | ✅ Yes       |
| **PyPI Cache**         | ✅ Used        | ❌ N/A       |

<!-- markdownlint-enable MD060 -->

### Docker Image Performance

| Metric            | Value                       |
| ----------------- | --------------------------- |
| **Build Time**    | ~10-15 minutes (multi-arch) |
| **Image Size**    | ~150 MB (compressed)        |
| **Architectures** | linux/amd64, linux/arm64    |
| **Registry**      | ghcr.io                     |
| **Caching**       | Layer caching enabled       |

---

## 🔄 Migration Guide

### ✅ No Breaking Changes

Existing workflows continue to work without modification. The action is
**100% backward compatible**.

### Automatic Upgrade Path

Update your version tag:

```yaml
# Before
- uses: lfreleng-actions/http-api-tool-docker@v0.1.2

# After (automatically uses uvx)
- uses: lfreleng-actions/http-api-tool-docker@v0.2.0
```

### Opt-in to Docker

If you prefer Docker deployment:

```yaml
- uses: lfreleng-actions/http-api-tool-docker@v0.2.0
  with:
    deploy: 'docker'  # Explicitly use Docker
```

See [MIGRATION.md](MIGRATION.md) for detailed migration instructions.

---

## 🐛 Bug Fixes

- Fixed type inconsistencies in action inputs (now all strings)
- Improved error handling for missing dependencies
- Better GitHub Actions output handling in both deployment modes

---

## 📚 Documentation

### New Documentation

- `MIGRATION.md`: Complete migration guide
- Example workflows demonstrating both deployment methods
- Performance comparison in README
- Deployment method decision guide

### Updated Documentation

- README: Added deployment methods section
- README: Updated inputs table with new options
- README: Added usage examples for both methods

---

## 🔐 Security

- Both deployment methods maintain the same security standards
- uvx installs packages with hash verification from PyPI
- Docker continues to use pinned versions with checksum validation
- No reduction in security posture

---

## 🎯 Use Cases

### When to Use uvx (Default)

- ✅ Most workflows
- ✅ When speed is important
- ✅ Standard GitHub Actions runners
- ✅ Public API testing

### When to Use Docker

- ✅ Need container isolation
- ✅ Custom network configurations
- ✅ Specific container security requirements
- ✅ Complex CA certificate mounting

---

## 📦 Package Information

### PyPI Package

- **Name**: `http-api-tool`
- **Version**: `0.2.0`
- **Python Support**: 3.10, 3.11, 3.12, 3.13
- **License**: Apache-2.0

### Docker Image

- **Registry**: `ghcr.io/lfreleng-actions/http-api-tool-docker`
- **Tags**: `v0.2.0`, `0.2`, `0`, `latest`
- **Platforms**: linux/amd64, linux/arm64
- **License**: Apache-2.0

---

## 🔮 What's Next

### Planned for v0.3.0

- More response validation options
- Enhanced metrics and reporting
- WebSocket support
- GraphQL endpoint testing
- Docker image multi-registry support (DockerHub)

---

## 📞 Support

- 📖 [Documentation](README.md)
- 🔄 [Migration Guide](MIGRATION.md)
- 🐛 [Issue Tracker](https://github.com/lfreleng-actions/http-api-tool-docker/issues)
- 💬 [Discussions](https://github.com/lfreleng-actions/http-api-tool-docker/discussions)

---

## ⚡ Quick Start

```yaml
# Fastest method (default - uvx)
- uses: lfreleng-actions/http-api-tool-docker@v0.2.0
  with:
    url: 'https://api.example.com/health'
    expected_http_code: '200'

# Or use the published Docker image directly
- name: Test API
  run: |
    docker run --rm \
      ghcr.io/lfreleng-actions/http-api-tool-docker:v0.2.0 \
      test --url https://api.example.com/health \
      --expected-http-code 200
```

That's it! The action will automatically use uvx for fast deployment, or you
can use the Docker image directly.
