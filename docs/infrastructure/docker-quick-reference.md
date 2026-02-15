---
layout: default
title: Docker Multi-Arch Quick Reference
description: Quick reference card for multi-architecture Docker builds
nav_order: 4
parent: Infrastructure
---

# Docker Multi-Architecture Quick Reference

## 📋 Common Commands

### Basic Building

```bash
# Build for current architecture
cd backend
docker build -f Dockerfile.fastapi -t financial-extractor:latest .

# Build for specific architecture
docker buildx build --platform linux/arm64 -t financial-extractor:arm64 .

# Build and load locally (single arch only)
docker buildx build --platform linux/amd64 --load -t financial-extractor:test .
```

### Multi-Architecture Building

```bash
# Build for AMD64 and ARM64
./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64

# Build and push to registry
./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64 --push --tag v1.0.0

# Build for all common architectures
./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64,linux/arm/v7

# Dry run (see what would happen)
./scripts/build-multiarch.sh --dry-run --platform linux/amd64,linux/arm64
```

### Testing

```bash
# Test current architecture
./scripts/test-architectures.sh

# Test specific architectures
./scripts/test-architectures.sh --architectures amd64,arm64

# Quick test (skip package verification)
./scripts/test-architectures.sh --quick

# Keep images after testing
./scripts/test-architectures.sh --keep-images

# Test camelot-py on ARM64
./scripts/test-camelot-arm64.sh
./scripts/investigate-camelot.sh
```

### Docker Compose

```bash
# Build and run
cd infrastructure/docker
docker compose -f docker-compose.multiarch.yml up --build

# Build only
docker compose -f docker-compose.multiarch.yml build

# Run in background
docker compose -f docker-compose.multiarch.yml up -d

# Stop and remove
docker compose -f docker-compose.multiarch.yml down
```

## 🔍 Inspection & Debugging

### Image Inspection

```bash
# Check what's in the image
docker run --rm financial-extractor:latest cat /app/build_info.txt

# Inspect image metadata
docker inspect financial-extractor:latest

# Check architecture
docker image inspect financial-extractor:latest --format '{{.Architecture}}'

# View build history
docker history financial-extractor:latest
```

### Multi-Arch Manifest

```bash
# View manifest (after pushing)
docker buildx imagetools inspect yourregistry/financial-extractor:latest

# Check available platforms
docker manifest inspect yourregistry/financial-extractor:latest
```

### Package Verification

```bash
# Check if package is available
docker run --rm financial-extractor:latest python -c "import camelot; print('✓')"

# List installed packages
docker run --rm financial-extractor:latest pip list

# Check Python version
docker run --rm financial-extractor:latest python --version
```

### Debugging Failed Builds

```bash
# Verbose build output
docker buildx build --progress=plain --no-cache -f Dockerfile.fastapi .

# Enter container for debugging
docker run -it --entrypoint /bin/bash financial-extractor:latest

# Check logs
docker logs <container-id>
```

## 🎯 Quick Fixes

### Problem: Build fails on ARM64

```bash
# Check exclusions config
grep -A20 "arch_exclusions.json" Dockerfile.fastapi

# Build with verbose output
docker buildx build --platform linux/arm64 --progress=plain . 2>&1 | tee build.log
```

### Problem: Package not found

```bash
# Verify package in virtual environment
docker run --rm financial-extractor:latest /app/.venv/bin/pip list | grep <package-name>

# Check if package should be excluded
docker run --rm financial-extractor:latest cat /tmp/arch_exclusions.json
```

### Problem: Health check failing

```bash
# Check if service is running
docker run -p 3030:3030 financial-extractor:latest

# Test health endpoint manually
curl http://localhost:3030/healthcheck
```

## 🛠️ Configuration

### Modify Architecture Exclusions

Edit the JSON in `Dockerfile.fastapi` (around line 40):

```json
{
  "arm64": {
    "exclude": ["package-name"],
    "reason": "Why it's excluded"
  }
}
```

### Add Optional Package

Add to the `optional_packages` dict in `Dockerfile.fastapi` (around line 151):

```python
'package-name[extras]': {
    'import_name': 'pkg',
    'description': 'What it does'
}
```

## 📦 Registry Operations

### Tag and Push

```bash
# Tag image
docker tag financial-extractor:latest registry.example.com/financial-extractor:v1.0.0

# Push single architecture
docker push registry.example.com/financial-extractor:v1.0.0

# Build and push multi-arch
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag registry.example.com/financial-extractor:v1.0.0 \
  --push \
  -f Dockerfile.fastapi \
  .
```

### Pull and Run

```bash
# Pull image (auto-detects architecture)
docker pull registry.example.com/financial-extractor:v1.0.0

# Run with environment variables
docker run -p 3030:3030 \
  -e DATABASE_URL=postgresql://... \
  registry.example.com/financial-extractor:v1.0.0
```

## 🔐 Security

### Scan for Vulnerabilities

```bash
# Using Docker scan
docker scan financial-extractor:latest

# Using Trivy
trivy image financial-extractor:latest

# Using Snyk
snyk container test financial-extractor:latest
```

### Check User

```bash
# Verify running as non-root
docker run --rm financial-extractor:latest whoami
# Should output: appuser
```

## 🎨 Development

### Hot Reload Mode

```bash
# Run with code mounted as volume
docker run -p 3030:3030 \
  -v $(pwd)/app:/app/app:ro \
  financial-extractor:latest \
  uvicorn run:application --reload --host 0.0.0.0
```

### Debug Mode

```bash
# Run with Python debugger
docker run -p 3030:3030 -it \
  financial-extractor:latest \
  python -m pdb -m uvicorn run:application --host 0.0.0.0
```

## 📊 Performance

### Check Build Cache

```bash
# View cache
ls -lh /tmp/.buildx-cache

# Clear cache
rm -rf /tmp/.buildx-cache
```

### Build with Cache

```bash
# Use cache mount
docker buildx build \
  --cache-from type=local,src=/tmp/.buildx-cache \
  --cache-to type=local,dest=/tmp/.buildx-cache \
  -t financial-extractor:latest \
  -f Dockerfile.fastapi \
  .
```

## 🔄 CI/CD Integration

### GitHub Actions

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

### GitLab CI

```yaml
build:
  script:
    - docker buildx build 
        --platform linux/amd64,linux/arm64
        --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
        --push
        -f backend/Dockerfile.fastapi
        backend/
```

## 💡 Tips & Tricks

### Speed Up Builds

```bash
# Use buildkit cache
export DOCKER_BUILDKIT=1

# Parallel builds
docker buildx build --platform linux/amd64,linux/arm64 ...
```

### Save Build Logs

```bash
# Save to file
docker buildx build . 2>&1 | tee build-$(date +%Y%m%d-%H%M%S).log
```

### Extract Files from Image

```bash
# Copy file from image
docker create --name temp financial-extractor:latest
docker cp temp:/app/build_info.txt .
docker rm temp
```

## 📱 Platform Detection

```bash
# Check your current platform
docker version --format '{{.Server.Arch}}'

# Check QEMU support
docker run --rm --privileged tonistiigi/binfmt

# List supported platforms
docker buildx ls
```

## 🆘 Emergency Commands

### Stop All Containers

```bash
docker stop $(docker ps -q)
```

### Remove All Test Images

```bash
docker rmi $(docker images 'test-arch-*' -q)
```

### Clean Everything

```bash
# Remove all stopped containers, unused networks, dangling images
docker system prune -a

# Remove build cache
docker builder prune -a
```

## 🎯 One-Liners

```bash
# Build, test, and push in one go
./scripts/test-architectures.sh && ./scripts/build-multiarch.sh --push

# Quick local test
docker build -t test . && docker run --rm test python -c "import fastapi; print('OK')"

# Check image size
docker images financial-extractor --format "{{.Repository}}:{{.Tag}} - {{.Size}}"

# Find largest layers
docker history financial-extractor:latest --no-trunc --format "{{.Size}}\t{{.CreatedBy}}" | sort -hr | head -10
```

## ✅ Checklist

Before deploying:
- [ ] Tested on target architectures
- [ ] Health check works
- [ ] Environment variables configured
- [ ] Volumes mounted correctly
- [ ] Resource limits set
- [ ] Security scan passed
- [ ] Documentation updated

**Pro Tip**: Bookmark this file for quick reference! 📌
