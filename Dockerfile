# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

# UV version and checksums for secure installation with architecture-aware download
# uv 0.8.4 - https://github.com/astral-sh/uv/releases/tag/0.8.4
#
# This Dockerfile automatically detects the target architecture (amd64/arm64) and
# downloads the appropriate uv binary with checksum validation to prevent MITM
# attacks.
#
# To override the version: docker build --build-arg UV_VERSION=0.8.3 .
# Supports: linux/amd64 (Intel/AMD x86_64) and linux/arm64 (Apple Silicon/ARM64)
ARG UV_VERSION=0.8.4
ARG UV_CHECKSUM_AMD64=eb61d39fdc6ea21a6d00a24b50376102168240849c5022d3eba331f972ba3934
ARG UV_CHECKSUM_ARM64=d42742a28ce161e72cce45c8c5621ee23317e30d461f595c382acf0f9b331f20

# Multi-stage build for optimized caching and smaller final image
FROM python:3.11-slim@sha256:7a3ed1226224bcc1fe5443262363d42f48cf832a540c1836ba8ccbeaadf8637c AS base

# Install system dependencies and create app user in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    iproute2 \
    libcurl4-openssl-dev \
    libssl-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# UV installer stage - eliminates duplication across build stages
FROM base AS uv-installer

# Inherit UV version and checksums from global args
ARG UV_VERSION
ARG UV_CHECKSUM_AMD64
ARG UV_CHECKSUM_ARM64
ARG TARGETARCH

# Install uv with architecture-aware download and checksum validation
# Automatically selects the correct binary and checksum based on TARGETARCH
RUN set -eu; \
    case "${TARGETARCH}" in \
        amd64) \
            UV_ARCH="x86_64-unknown-linux-gnu"; \
            UV_CHECKSUM="${UV_CHECKSUM_AMD64}"; \
            ;; \
        arm64) \
            UV_ARCH="aarch64-unknown-linux-gnu"; \
            UV_CHECKSUM="${UV_CHECKSUM_ARM64}"; \
            ;; \
        *) \
            echo "Unsupported architecture: ${TARGETARCH}"; \
            exit 1; \
            ;; \
    esac; \
    curl -LsSf "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_ARCH}.tar.gz" -o uv.tar.gz && \
    echo "${UV_CHECKSUM}  uv.tar.gz" | sha256sum -c - && \
    tar -xzf uv.tar.gz && \
    mv "uv-${UV_ARCH}/uv" /usr/local/bin/ && \
    mv "uv-${UV_ARCH}/uvx" /usr/local/bin/ && \
    rm -rf uv.tar.gz "uv-${UV_ARCH}" && \
    uv --version

# Build stage for dependencies
FROM base AS deps

# Copy uv binaries from installer stage
COPY --from=uv-installer /usr/local/bin/uv /usr/local/bin/uv
COPY --from=uv-installer /usr/local/bin/uvx /usr/local/bin/uvx

# Copy project files for dependency resolution
COPY pyproject.toml README.md ./

# Copy full source tree to permit version detection during uv lock
COPY src/ src/

# Generate uv.lock from pyproject.toml during build to ensure freshness
# This prevents stale package versions from being baked into the container
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock

# Install dependencies using the freshly generated lock file
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Production stage
FROM base AS production

# Copy uv binaries from installer stage
COPY --from=uv-installer /usr/local/bin/uv /usr/local/bin/uv
COPY --from=uv-installer /usr/local/bin/uvx /usr/local/bin/uvx

# Copy the virtual environment and lock file from deps stage
COPY --from=deps /app/.venv /app/.venv
COPY --from=deps /app/uv.lock ./

# Copy source code and project configuration
COPY src/ src/
COPY pyproject.toml README.md ./

# Install the package itself using proper uv installation for correct handling
# of entry points, dependencies, and metadata
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Note: For GitHub Actions Docker containers that need to write to environment
# files, running as root is necessary due to file permission requirements.
# This is a common pattern in GitHub Actions Docker containers.

# Activate the virtual environment permanently for the container
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

# Set entrypoint to use the installed package from virtual environment
ENTRYPOINT ["/app/.venv/bin/python", "-m", "http_api_tool"]
