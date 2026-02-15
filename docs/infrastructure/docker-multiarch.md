---
layout: default
title: Multi-Architecture Docker Builds
description: Guide for building Docker images across multiple CPU architectures (AMD64, ARM64)
nav_order: 3
parent: Infrastructure
---

# Multi-Architecture Docker Build Guide

This guide explains how to build Docker images for multiple CPU architectures, handle architecture-specific package compatibility, and deploy across different platforms.

## Overview

The project uses architecture-aware Docker builds to support both AMD64 and ARM64 platforms. Some packages (like `camelot-py`) may not have wheels available for all architectures, so the build process automatically excludes incompatible packages based on the target architecture.

## Quick Start

### Setup Environment

```bash
cd backend
./scripts/setup.sh
```

This will:

- Check Docker and Docker Buildx
- Install QEMU for cross-platform emulation
- Create a multi-architecture builder
- Set up build cache

### Build for Multiple Architectures

```bash
# Build for AMD64 and ARM64
./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64

# Build and push to registry
./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64 --push --tag v1.0.0

# Build for specific architecture only
./scripts/build-multiarch.sh --platform linux/arm64 --load
```

### Test Different Architectures

```bash
# Test builds on multiple architectures
./scripts/test-architectures.sh --architectures amd64,arm64

# Quick test (skip package verification)
./scripts/test-architectures.sh --quick
```

## Architecture Support Matrix

| Architecture   | Status             | Notes                  |
| -------------- | ------------------ | ---------------------- |
| `linux/amd64`  | ✅ Full support    | All packages available |
| `linux/arm64`  | ⚠️ Partial support | Excludes camelot-py    |
| `linux/arm/v7` | ⚠️ Partial support | Excludes camelot-py    |
| `linux/386`    | ✅ Full support    | All packages available |

## How It Works

### Architecture Detection

The Dockerfile uses Docker's built-in `TARGETARCH` variable to automatically detect the target architecture:

```dockerfile
ARG TARGETARCH  # Automatically: amd64, arm64, arm, 386, etc.
```

### Package Exclusion Configuration

Architecture-specific exclusions are defined in a JSON configuration within the Dockerfile:

```json
{
  "arm64": {
    "exclude": ["camelot-py"],
    "reason": "No ARM64 wheels for pdftopng dependency"
  },
  "amd64": {
    "exclude": []
  }
}
```

### Build Process Flow

1. Docker detects `TARGETARCH` (e.g., "arm64")
2. Python script loads JSON config for that architecture
3. Removes incompatible packages from `pyproject.toml`
4. Installs core dependencies with `uv`
5. Attempts optional packages only on compatible architectures
6. Verifies critical imports work
7. Copies to runtime stage

## Testing camelot-py Compatibility

If you want to test whether `camelot-py` works on ARM64 (it might work now even though it's excluded):

```bash
# Quick test (30 seconds)
./scripts/test-camelot-arm64.sh

# Detailed investigation (2 minutes)
./scripts/investigate-camelot.sh
```

Based on the results:

- **If tests pass**: You can remove `camelot-py` from exclusions
- **If tests fail**: Keep the exclusions as they are

See [Decision Guide](#decision-guide) below for more details.

## Using Docker Compose

The multi-architecture Docker Compose file is located at:

```
infrastructure/docker/docker-compose.multiarch.yml
```

### Basic Usage

```bash
# Build for current architecture
cd infrastructure/docker
docker compose -f docker-compose.multiarch.yml build

# Build and run
docker compose -f docker-compose.multiarch.yml up --build

# Build for specific architecture
docker compose -f docker-compose.multiarch.yml build --build-arg TARGETARCH=arm64
```

## Build Scripts

### build-multiarch.sh

Build Docker images for multiple architectures:

```bash
./scripts/build-multiarch.sh [options]

Options:
  --platform <platforms>  Comma-separated platforms (default: linux/amd64,linux/arm64)
  --tag <tag>            Image tag (default: latest)
  --dockerfile <file>    Dockerfile to use (default: Dockerfile.fastapi)
  --push                 Push to registry after build
  --load                 Load image into local Docker (single platform only)
  --dry-run              Show commands without executing
  --help                 Show help message
```

### test-architectures.sh

Test Docker builds across multiple architectures:

```bash
./scripts/test-architectures.sh [options]

Options:
  --architectures <archs>  Comma-separated architectures (default: amd64,arm64)
  --dockerfile <file>      Dockerfile to test (default: Dockerfile.fastapi)
  --quick                  Skip package verification (faster)
  --keep-images            Don't remove test images after testing
  --help                   Show help message
```

## Adding New Optional Dependencies

To add a new optional dependency that may not work on all architectures:

### Step 1: Update the JSON configuration

Edit the `arch_exclusions.json` section in `Dockerfile.fastapi`:

```json
{
  "arm64": {
    "exclude": ["camelot-py", "your-new-package"],
    "reason": "No ARM64 wheels available"
  }
}
```

### Step 2: Add to optional packages list

Update the `optional_packages` dictionary in the Dockerfile:

```python
optional_packages = {
    'camelot-py[base]': {
        'import_name': 'camelot',
        'description': 'PDF table extraction'
    },
    'your-new-package': {
        'import_name': 'your_package',
        'description': 'What it does'
    }
}
```

### Step 3: Test it

```bash
./scripts/test-architectures.sh --architectures amd64,arm64
```

## Decision Guide: Should You Exclude camelot-py?

### Quick Test

Run these tests to determine if `camelot-py` works on Linux ARM64:

```bash
# Quick test (30 seconds)
./scripts/test-camelot-arm64.sh

# Detailed investigation (2 minutes)
./scripts/investigate-camelot.sh
```

### Decision Tree

- **If tests PASS** ✅:

  - Remove `camelot-py` from exclusions
  - Add required system packages (`ghostscript`, `poppler-utils`)
  - Update Dockerfile to include camelot on all platforms

- **If tests FAIL** ❌:
  - Keep exclusions as they are
  - Document the limitation
  - Ensure your app handles missing camelot gracefully

### Why macOS ARM64 ≠ Linux ARM64

Even though both are ARM64:

- **macOS ARM64**: Uses Darwin OS, macOS-specific wheels, Homebrew packages
- **Linux ARM64**: Uses Linux OS, needs `manylinux_aarch64` wheels, apt packages

A package working on your Mac doesn't guarantee it works in Linux Docker containers.

## Debugging Build Issues

### Enable Verbose Output

```bash
docker buildx build --progress=plain --no-cache -f Dockerfile.fastapi .
```

### Check Architecture Detection

```bash
# Inspect built image
docker run --rm <image> cat /app/build_info.txt

# Check image architecture
docker image inspect <image> --format '{{.Architecture}}'
```

### Test Package Installation

```bash
# Enter container
docker run -it --entrypoint /bin/bash <image>

# Check installed packages
pip list | grep camelot

# Test import
python -c "import camelot; print('OK')"
```

## Best Practices

1. **Always Use BuildKit**: `export DOCKER_BUILDKIT=1`
2. **Use Layer Caching**: Cache mounts speed up rebuilds
3. **Test on Multiple Architectures**: Don't assume compatibility
4. **Document Limitations**: Clearly state which features work on which platforms
5. **Graceful Degradation**: Make sure your app handles missing optional dependencies

## Security Considerations

- ✅ Non-root user: Application runs as `appuser` (UID 1000)
- ✅ Minimal base image: Uses `python:3.13-slim`
- ✅ No cache leakage: Cache cleared after installation
- ✅ Signed images: Support for Docker Content Trust
- ✅ Vulnerability scanning: Compatible with `docker scan` and Trivy

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Build multi-arch
  run: |
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      --tag ${{ secrets.REGISTRY }}/financial-extractor:${{ github.sha }} \
      --push \
      -f backend/Dockerfile.fastapi \
      backend/
```

## Additional Resources

- [Docker BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [Multi-platform Builds](https://docs.docker.com/build/building/multi-platform/)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/configure-ci-cd/)

## Troubleshooting

### Build fails on ARM64

```bash
# Check what was excluded
docker buildx build --platform linux/arm64 --progress=plain . 2>&1 | grep -A5 "exclusions"
```

### Package not found

```bash
# Verify package in virtual environment
docker run --rm <image> /app/.venv/bin/pip list | grep <package-name>
```

### Health check failing

```bash
# Test health endpoint manually
docker run -p 3030:3030 <image>
curl http://localhost:3030/healthcheck
```

## Summary

The multi-architecture build system provides:

- ✅ Smooth multi-architecture builds
- ✅ Clear, maintainable configuration
- ✅ Helpful build and test scripts
- ✅ Better error messages
- ✅ Production-ready setup

The architecture pain point is solved! 🚀
