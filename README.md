<!--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: 2025 The Linux Foundation
-->

# HTTP API Test Tool

An HTTP API testing tool for GitHub Actions and command-line usage.

This action performs HTTP requests with configurable verification of response
status, content, headers, and timing. Implemented in Python to modern PEP
standards, using Typer and pycurl. Avoids JSON escaping issues associated with
shell code implementations in GitHub actions.

## http-api-tool-docker

A containerized version of the HTTP API test tool with secure,
multi-architecture support.

### Published Docker Images

Pre-built, multi-architecture Docker images are automatically published to
GitHub Container Registry on every release:

```bash
# Pull the latest version
docker pull ghcr.io/lfreleng-actions/http-api-tool-docker:latest

# Pull a specific version
docker pull ghcr.io/lfreleng-actions/http-api-tool-docker:0.2.0

# Use directly in commands
docker run --rm ghcr.io/lfreleng-actions/http-api-tool-docker:latest test \
  --url https://api.example.com/health \
  --expected-http-code 200
```

**Available Tags:**

- `latest` - Most recent release
- `X.Y.Z` - Specific version (e.g., `0.2.0`, from the `v0.2.0` release)
- `X.Y` - Minor version (e.g., `0.2`)
- `X` - Major version (e.g., `0`)

**Supported Platforms:**

- `linux/amd64` (Intel/AMD x86_64)
- `linux/arm64` (Apple Silicon/ARM64)

### Docker Security Features

The Containerfile implements these security best practices:

- **Version Pinning**: uv binary version is explicitly pinned (0.8.4)
- **Checksum Validation**: Downloads verify against SHA256 checksums to
  prevent MITM attacks
- **Multi-Architecture Support**: Automatically detects and downloads the
  correct binary for:
  - `linux/amd64` (Intel/AMD x86_64)
  - `linux/arm64` (Apple Silicon/ARM64)

### Building the Container (Optional)

You can build the container locally if needed, though pre-built images are available:

```bash
# Build for current platform
docker build -f docker/Containerfile -t http-api-tool .

# Build for specific platform
docker build -f docker/Containerfile --platform linux/amd64 -t http-api-tool .
docker build -f docker/Containerfile --platform linux/arm64 -t http-api-tool .

# Override uv version
docker build -f docker/Containerfile --build-arg UV_VERSION=0.8.5 \
  -t http-api-tool .
```

### Container Usage

```bash
# Using published image
docker run --rm ghcr.io/lfreleng-actions/http-api-tool-docker:latest --help

# Test an API endpoint
docker run --rm ghcr.io/lfreleng-actions/http-api-tool-docker:latest test \
  --url https://api.example.com/health \
  --expected-http-code 200

# Using locally built image
docker run --rm http-api-tool --help

# Check uv version in container
docker run --rm --entrypoint=/usr/local/bin/uv \
  ghcr.io/lfreleng-actions/http-api-tool-docker:latest --version
```

## Features

- **Supported HTTP Methods**: Supports GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Authentication**: Basic Auth via auth_string and custom headers support
- **Response Validation**: Status code, regex pattern matching, response time limits
- **Retry Logic**: Exponential backoff, doubling up to a configurable cap
- **Dual Usage**: Works as both a CLI tool and GitHub Action
- **Robust Error Handling**: Detailed error messages and proper exit codes
- **JSON Safety**: Uses pycurl instead of shell commands to avoid escaping issues
- **SSL/TLS Support**: Full SSL verification with custom CA bundle support
- **Response Metrics**: Comprehensive timing and size measurements

## Usage

### As a GitHub Action

The action supports two deployment methods:

#### 1. uvx Deployment (Default - Fast & Recommended)

Uses `uvx` to run the tool directly from PyPI without building a container.
This is faster and is the recommended method.

```yaml
- name: Test API Endpoint (uvx - default)
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    url: 'https://api.example.com/health'
    http_method: 'GET'
    expected_http_code: '200'
    curl_timeout: '30'
    max_response_time: '10'
    retries: '3'
    initial_sleep_time: '2'

# Explicitly specify uvx
- name: Test API with uvx
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    deploy: 'uvx'
    url: 'https://api.example.com/health'
    expected_http_code: '200'
```

The uvx path runs `http-api-tool` on its own uv-managed Python 3.13,
installed under `runner.temp`. No caller setting chooses that
interpreter: the choice ignores `PATH`, `UV_PYTHON`, `VIRTUAL_ENV`,
`CONDA_PREFIX`, the `PYTHON*` variables and uv settings in the
workspace. Package index, credential, proxy and certificate settings
(`UV_INDEX*`, `UV_DEFAULT_INDEX`, `UV_EXTRA_INDEX_URL`,
`UV_KEYRING_PROVIDER`, `UV_INSECURE_HOST`, `UV_HTTP_TIMEOUT`, the
`*_PROXY` variables, `SSL_CERT_FILE`, `SSL_CERT_DIR` and
`UV_NATIVE_TLS`) still reach uv. The package install also sees the
rest of the caller's environment, `PATH` included, less any other
`UV_*` setting and the `PYTHON*`, `VIRTUAL_ENV` and `CONDA_*`
variables, so under `UV_KEYRING_PROVIDER=subprocess` uv finds the
caller's `keyring` executable and it finds the variables it reads.
The exception is
`use_local_code: true`, which runs the `http-api-tool` found on
`PATH`, so the caller installs it and picks its interpreter.

The action trusts the caller's `PATH`. The runner finds `bash` on it
for every step, and `setup-uv` runs its helpers from it, so a caller
that puts a directory from its checkout on `PATH` is outside what a
composite action can defend against.

#### 2. Docker Deployment (Containerized)

Uses Docker to run the tool in a container. This is useful when you need
isolation or specific container features.

```yaml
- name: Test API Endpoint (Docker)
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    deploy: 'docker'
    url: 'https://api.example.com/health'
    http_method: 'GET'
    expected_http_code: '200'
    curl_timeout: '30'
    max_response_time: '10'
    retries: '3'
    initial_sleep_time: '2'

# Example with custom CA certificate
- name: Test API with Custom CA
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    deploy: 'docker'
    url: 'https://internal-api.company.com/health'
    ca_bundle_path: '/path/to/ca-certificates.pem'
    expected_http_code: '200'
```

**Deployment Method Comparison:**

<!-- markdownlint-disable MD060 -->

| Feature   | uvx (default)  | docker                     |
| --------- | -------------- | -------------------------- |
| Speed     | ⚡ Fast (~10s) | 🐌 Slower (~60s for build) |
| Isolation | Process-level  | Container-level            |
| Caching   | PyPI cache     | Docker layer cache         |
| Use Case  | Most scenarios | Special isolation needs    |

<!-- markdownlint-enable MD060 -->

### As a CLI Tool

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies using UV with hash verification
uv sync --frozen --no-dev

# Basic usage
uv run python -m http_api_tool test --url https://api.example.com/health

# Advanced usage
uv run python -m http_api_tool test \
  --url https://api.example.com/users \
  --http-method POST \
  --request-body '{"name": "John", "email": "john@example.com"}' \
  --request-headers '{"Content-Type": "application/json"}' \
  --auth-string username:password \
  --expected-http-code 201 \
  --regex '"id":\s*\d+' \
  --curl-timeout 30 \
  --max-response-time 10 \
  --retries 3
```

## Inputs

<!-- markdownlint-disable MD013 -->

| Input                   | Description                                                          | Required | Default            |
| ----------------------- | -------------------------------------------------------------------- | -------- | ------------------ |
| `deploy`                | Deployment method: `uvx` (fast, default) or `docker` (containerized) | No       | `uvx`              |
| `python_version`        | Ignored: deploy=uvx runs on a uv-managed Python 3.13                 | No       | `3.11`             |
| `url`                   | URL of API server/interface to check                                 | Yes      | -                  |
| `auth_string`           | Authentication string, colon separated username/password             | No       | -                  |
| `service_name`          | Name of HTTP/HTTPS API service tested                                | No       | `API Service`      |
| `initial_sleep_time`    | Delay in seconds before the first retry, doubling thereafter         | No       | `1`                |
| `max_delay`             | Max delay in seconds between retries                                 | No       | `30`               |
| `retries`               | Number of retries before declaring service unavailable               | No       | `3`                |
| `expected_http_code`    | HTTP response code to accept from the API service                    | No       | `200`              |
| `regex`                 | Verify server response with regular expression                       | No       | -                  |
| `show_header_json`      | Display response header as JSON in action output                     | No       | `false`            |
| `curl_timeout`          | Max time in seconds for cURL to wait for a response                  | No       | `5`                |
| `http_method`           | HTTP method to use (GET, POST, PUT, etc.)                            | No       | `GET`              |
| `request_body`          | Data to send with POST/PUT/PATCH requests                            | No       | -                  |
| `content_type`          | Content type for the request body                                    | No       | `application/json` |
| `request_headers`       | Custom HTTP headers sent in JSON format                              | No       | -                  |
| `verify_ssl`            | Verify SSL certificates                                              | No       | `true`             |
| `ca_bundle_path`        | Path to CA bundle file for SSL verification                          | No       | -                  |
| `include_response_body` | Include response body in outputs (base64)                            | No       | `false`            |
| `follow_redirects`      | Follow HTTP redirects                                                | No       | `true`             |
| `max_response_time`     | Max acceptable response time in seconds                              | No       | `0`                |
| `connection_reuse`      | Reuse connections between requests                                   | No       | `true`             |
| `debug`                 | Enables debugging output                                             | No       | `false`            |
| `fail_on_timeout`       | Fail if response time exceeds max_response_time                      | No       | `false`            |

<!-- markdownlint-enable MD013 -->

## Outputs

<!-- markdownlint-disable MD013 -->

| Output                   | Description                                                |
| ------------------------ | ---------------------------------------------------------- |
| `time_delay`             | Number of seconds waiting for service availability/failure |
| `response_http_code`     | HTTP response code received from the server                |
| `response_header_json`   | HTTP response header as JSON                               |
| `response_header_size`   | HTTP response header size in bytes                         |
| `response_body_size`     | HTTP response body size in bytes                           |
| `regex_match`            | Whether the regular expression matched the server reply    |
| `response_body_base64`   | Response body base64 encoded (when enabled)                |
| `total_time`             | Total time for the request in seconds                      |
| `connect_time`           | Time to establish connection in seconds                    |
| `response_time_exceeded` | Whether response time exceeded max time                    |

<!-- markdownlint-enable MD013 -->

## Authentication

### Authentication String

```yaml
with:
  auth_string: 'username:password'
```

### Custom Headers

```yaml
with:
  request_headers: |
    {
      "Authorization": "Bearer your-jwt-token",
      "X-API-Key": "your-api-key",
      "X-Custom-Header": "value"
    }
```

## Examples

### Simple Health Check

```yaml
- name: Health Check
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    url: 'https://api.example.com/health'
    expected_http_code: '200'
```

### POST with JSON Data

```yaml
- name: Create User
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    url: 'https://api.example.com/users'
    http_method: 'POST'
    request_headers: '{"Content-Type": "application/json"}'
    request_body: '{"name": "John Doe", "email": "john@example.com"}'
    expected_http_code: '201'
    regex: '"id":\s*\d+'
```

### Authenticated Request with Retry

```yaml
- name: Get Protected Resource
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    url: 'https://api.example.com/protected'
    request_headers: '{"Authorization": "Bearer ${{ secrets.API_TOKEN }}"}'
    retries: '5'
    initial_sleep_time: '2'
    curl_timeout: '30'
```

### Response Validation

```yaml
- name: Test API Response
  uses: lfreleng-actions/http-api-tool-docker@main
  with:
    url: 'https://api.example.com/status'
    regex: '"status":\s*"ok"'
    max_response_time: '5'
```

## Error Handling

The action provides detailed error messages for common scenarios:

- **Connection Errors**: Network connectivity issues
- **Timeout Errors**: Request or connection timeouts
- **Authentication Errors**: Invalid credentials
- **Validation Errors**: Unexpected status codes or response patterns
- **SSL Errors**: Certificate verification failures

## Development

### Running Tests

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies with hash verification
uv sync --frozen

# Run tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=http_api_tool --cov-report=html
```

### Integration Testing

The project includes a comprehensive integration test suite:

```bash
# Run all tests including integration tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=http_api_tool --cov-report=html
```

The test suite validates:

- Version display and help output
- All HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response handling
- Custom headers support
- Regex pattern matching
- Response time validation
- Retry logic with backoff
- HTTPS with SSL/TLS certificate validation

### Continuous Integration

The GitHub Actions workflows call the organisation's reusable workflow
families for the generic stages; the jobs they define themselves are the
ones specific to this tool.

`build-test.yaml` runs on pull requests and pushes to `main`:

- [python-workflows `build-test.yaml`][python-workflows]: Python build,
  tests, dependency audit, SBOM and Grype scan. The Grype gate arms when
  the change touched a dependency file (`grype_gate_when:
  dependencies-changed`) and fails on fixable findings in declared
  dependencies from medium up and on critical findings in transitive ones.
  Setting the `NO_BLOCK_AUDIT_FAIL` repository variable to `true` lets a
  failing dependency audit report without blocking, on both workflows.
- [docker-workflows `build-test.yaml`][docker-workflows]: container build
  from `docker/Containerfile`, a `--help` smoke test, hadolint (configured
  in `.hadolint.yaml`), image SBOM and Grype scan. The two family calls
  run in parallel, so this one sets `grype_cache_db` to restore the Grype
  database cache without saving it, leaving the Python call as the single
  writer.
- Tool-specific jobs: action integration tests against `go-httpbin`, CLI
  tests, deployment-mode tests (uvx and Docker), workspace isolation and
  private index credential checks for the uvx path, Docker integration
  tests, bandit static analysis, and the GHCR publish of `latest` on
  pushes to `main`.

`build-test-release.yaml` runs on tag pushes:

- [python-workflows `build-test-release.yaml`][python-workflows]: tag
  validation, signed and attested build, tests, audit, SBOM, Grype scan,
  artefact attachment and GitHub release promotion.
- Test PyPI and PyPI publishing, then the multi-architecture image push to
  GHCR with the `X.Y.Z`, `X.Y`, `X` and `latest` tags; the image tags omit
  the release tag's leading `v`, so release `v1.2.3` publishes `1.2.3`.

Every custom job loads the organisation egress allow-list through
`harden-runner-block-action` and runs `harden-runner` in block mode.

[python-workflows]: https://github.com/lfreleng-actions/python-workflows
[docker-workflows]: https://github.com/lfreleng-actions/docker-workflows

### Pre-commit Hooks

```bash
# Install pre-commit (included in dev dependencies)
uv sync --frozen

# Install hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

### Docker Requirements Management

The Docker image uses a **dynamic requirements generation** approach where the
Docker build process generates the `requirements-docker.txt` file to
ensure correct platform compatibility.

If you need to manually regenerate for local development:

```bash
# Regenerate requirements-docker.txt with all dependencies and hashes
# Note: This project now uses UV for dependency management
# The Containerfile uses UV directly, so requirements-docker.txt is no longer needed
# UV lock file (uv.lock) is automatically generated and used during builds

# Test the Docker build
docker build -f docker/Containerfile . --platform linux/arm64 -t http-api-tool-test
```

The `requirements-docker.txt` file contains:

- UV handles dependency resolution and locking automatically
- SHA256 hashes in uv.lock file
- Security protection against supply chain attacks
- Ensures reproducible Docker builds

**When to regenerate:**

- Updating dependencies in the project
- Docker build failures with hash verification errors
- Setting up the project for the first time
- After changes to `pyproject.toml` affecting dependencies
  (run `uv lock` to regenerate lock file)

### Local Development

```bash
# Test CLI functionality
uv run python -m http_api_tool test --help

# Test against local server
python -m http.server 8000 &
uv run python -m http_api_tool test --url http://localhost:8000
```

### Testing with go-httpbin Service

For testing HTTP API functionality, you can either use the go-httpbin GitHub
Action for workflows or set up a local go-httpbin service for development.

#### Using the go-httpbin GitHub Action

For GitHub Actions workflows, use the standalone go-httpbin action to set up an
HTTPS testing service:

<!-- markdownlint-disable MD013 -->

```yaml
steps:
  - name: Setup go-httpbin HTTPS service
    uses: lfreleng-actions/go-httpbin-action@692bf3b759b746041e9cc2eebec5a6006e6d6041 # v0.1.7
    id: httpbin
    with:
      debug: 'true'
      port: '8080'

  - name: Test API with go-httpbin
    uses: lfreleng-actions/http-api-tool-docker@main
    with:
      url: 'https://localhost:8080/get'
      ca_bundle_path: '${{ steps.httpbin.outputs.ca-cert-path }}'
      expected_http_code: '200'
```

<!-- markdownlint-enable MD013 -->

#### Using Local go-httpbin Service for Development

For local development and testing:

```bash
# Build Docker image
docker build -f docker/Containerfile -t http-api-tool .

# Run container
docker run --rm http-api-tool test \
  --url https://example.com/api \
  --expected-http-code 200
```

The local go-httpbin service provides all the same endpoints as httpbin.org
but runs locally for faster, more reliable testing.

The `setup-go-httpbin` target automatically:

- Installs mkcert if not present
- Creates a local Certificate Authority (CA)
- Generates SSL certificates for localhost
- Saves the CA certificate as `mkcert-ca.pem` in the project root
- Starts the go-httpbin service with proper HTTPS support

This ensures that SSL certificate validation remains enabled for all tests,
providing a more realistic testing environment.

## Migration from Shell Version

If you're migrating from the original shell-based implementation:

1. **Input Compatibility**: Most inputs remain the same with updated naming
2. **Output Compatibility**: Outputs are similar with enhanced information
3. **Behavior Changes**:
   - Better JSON handling (no more escaping issues)
   - More robust error reporting
   - Improved retry logic with exponential backoff
   - Better SSL/TLS handling
   - Enhanced debugging output
   - More comprehensive response metrics

## Package Management with UV

This project uses UV (fast Python package installer and resolver) for
dependency management:

### For Development

Install dependencies with:

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
uv sync --frozen
```

Run unit tests with:

```bash
uv run pytest tests/ -v
```

## Requirements

- Python 3.11+
- UV (Fast Python package installer and resolver)
- pycurl
- typer (for CLI usage)

UV manages dependencies, with hash-verified lock files for reproducible builds.

## License

Apache-2.0 License. See [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality (use `uv run pytest`)
5. Run pre-commit hooks
6. Submit a pull request
