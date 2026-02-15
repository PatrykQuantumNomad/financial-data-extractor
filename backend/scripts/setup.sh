#!/usr/bin/env bash
# setup.sh - Quick setup for multi-architecture Docker builds
#
# This script prepares your environment for building Docker images
# across multiple CPU architectures.

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Multi-Architecture Docker Setup      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x build-multiarch.sh test-architectures.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts are now executable${NC}\n"

# Check Docker
echo -e "${BLUE}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ $DOCKER_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not found. Please install Docker first.${NC}"
    echo -e "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Buildx
echo -e "\n${BLUE}Checking Docker Buildx...${NC}"
if docker buildx version &> /dev/null; then
    BUILDX_VERSION=$(docker buildx version)
    echo -e "${GREEN}✅ $BUILDX_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Docker Buildx not found. Installing...${NC}"
    docker buildx install || {
        echo -e "${YELLOW}⚠️  Could not install buildx automatically.${NC}"
        echo -e "   Please install manually: https://docs.docker.com/buildx/working-with-buildx/"
        exit 1
    }
fi

# Setup QEMU for multi-platform emulation
echo -e "\n${BLUE}Setting up QEMU for multi-platform builds...${NC}"
if docker run --rm --privileged tonistiigi/binfmt --install all &>/dev/null; then
    echo -e "${GREEN}✅ QEMU installed successfully${NC}"
    echo -e "   Supported platforms:"
    docker run --rm --privileged tonistiigi/binfmt | grep "enabled" | sed 's/^/   - /'
else
    echo -e "${YELLOW}⚠️  Could not install QEMU${NC}"
    echo -e "   Multi-platform builds may not work"
fi

# Create buildx builder
echo -e "\n${BLUE}Setting up buildx builder...${NC}"
BUILDER_NAME="multiarch-builder"
if docker buildx inspect "$BUILDER_NAME" &>/dev/null; then
    echo -e "${GREEN}✅ Builder '$BUILDER_NAME' already exists${NC}"
else
    echo -e "${BLUE}Creating new builder: $BUILDER_NAME${NC}"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
    docker buildx inspect --bootstrap
    echo -e "${GREEN}✅ Builder created and bootstrapped${NC}"
fi

# Set as current builder
docker buildx use "$BUILDER_NAME" 2>/dev/null || true

# Show available platforms
echo -e "\n${BLUE}Available build platforms:${NC}"
docker buildx inspect --bootstrap | grep "Platforms:" | sed 's/Platforms://' | tr ',' '\n' | sed 's/^/   ✓ /'

# Create cache directory
echo -e "\n${BLUE}Setting up build cache...${NC}"
mkdir -p /tmp/.buildx-cache
echo -e "${GREEN}✅ Cache directory ready: /tmp/.buildx-cache${NC}"

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Complete! 🎉                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Quick Start Commands:${NC}"
echo -e ""
echo -e "  1. Test your setup:"
echo -e "     ${YELLOW}./scripts/test-architectures.sh --quick${NC}"
echo -e ""
echo -e "  2. Build for multiple architectures:"
echo -e "     ${YELLOW}./scripts/build-multiarch.sh --platform linux/amd64,linux/arm64${NC}"
echo -e ""
echo -e "  3. Build specific Dockerfile:"
echo -e "     ${YELLOW}./scripts/build-multiarch.sh --dockerfile Dockerfile.celery${NC}"
echo -e ""

echo -e "${GREEN}Your environment is ready for multi-architecture builds!${NC}\n"
