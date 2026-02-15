#!/usr/bin/env bash
# build-multiarch.sh - Build Docker images for multiple architectures
#
# Usage:
#   ./build-multiarch.sh [options]
#
# Options:
#   --platform <platforms>  Comma-separated list of platforms (default: linux/amd64,linux/arm64)
#   --tag <tag>            Image tag (default: latest)
#   --target <target>      Build target: api or worker (default: api)
#   --push                 Push to registry after build
#   --load                 Load image into local Docker (only works with single platform)
#   --dry-run              Show commands without executing
#   --help                 Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PLATFORMS="linux/amd64,linux/arm64"
TAG="latest"
PUSH=false
LOAD=false
DRY_RUN=false
IMAGE_NAME="financial-data-extractor"
TARGET="api"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORMS="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --target)
            TARGET="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --load)
            LOAD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            grep '^#' "$0" | cut -c 2-
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate configuration
if $LOAD && $PUSH; then
    echo -e "${RED}Error: Cannot use --load and --push together${NC}"
    exit 1
fi

if $LOAD && [[ "$PLATFORMS" == *","* ]]; then
    echo -e "${RED}Error: --load only works with a single platform${NC}"
    echo "Specify one platform with: --platform linux/amd64"
    exit 1
fi

if [[ "$TARGET" != "api" && "$TARGET" != "worker" ]]; then
    echo -e "${RED}Error: --target must be 'api' or 'worker'${NC}"
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found in current directory${NC}"
    exit 1
fi

# Build metadata
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")

# Print build configuration
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Multi-Architecture Docker Build${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Image:      ${GREEN}${IMAGE_NAME}-${TARGET}:${TAG}${NC}"
echo -e "Target:     ${GREEN}${TARGET}${NC}"
echo -e "Platforms:  ${GREEN}${PLATFORMS}${NC}"
echo -e "Version:    ${GREEN}${VERSION}${NC}"
echo -e "Commit:     ${GREEN}${VCS_REF}${NC}"
echo -e "Build Date: ${GREEN}${BUILD_DATE}${NC}"
echo -e "Push:       ${GREEN}${PUSH}${NC}"
echo -e "Load:       ${GREEN}${LOAD}${NC}"
echo -e "${BLUE}============================================${NC}"

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}Error: docker buildx is not available${NC}"
    echo "Install it with: docker buildx install"
    exit 1
fi

# Create or use existing builder
BUILDER_NAME="multiarch-builder"
if ! docker buildx inspect "$BUILDER_NAME" &> /dev/null; then
    echo -e "${YELLOW}Creating new builder: ${BUILDER_NAME}${NC}"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
    docker buildx inspect --bootstrap
else
    echo -e "${GREEN}Using existing builder: ${BUILDER_NAME}${NC}"
    docker buildx use "$BUILDER_NAME"
fi

# Build command
BUILD_CMD="docker buildx build"
BUILD_CMD="$BUILD_CMD --platform $PLATFORMS"
BUILD_CMD="$BUILD_CMD --file Dockerfile"
BUILD_CMD="$BUILD_CMD --target $TARGET"
BUILD_CMD="$BUILD_CMD --tag $IMAGE_NAME-$TARGET:$TAG"
BUILD_CMD="$BUILD_CMD --build-arg BUILD_DATE=$BUILD_DATE"
BUILD_CMD="$BUILD_CMD --build-arg VCS_REF=$VCS_REF"
BUILD_CMD="$BUILD_CMD --build-arg VERSION=$VERSION"

# Add cache configuration for faster builds
BUILD_CMD="$BUILD_CMD --cache-from type=local,src=/tmp/.buildx-cache"
BUILD_CMD="$BUILD_CMD --cache-to type=local,dest=/tmp/.buildx-cache,mode=max"

if $PUSH; then
    BUILD_CMD="$BUILD_CMD --push"
elif $LOAD; then
    BUILD_CMD="$BUILD_CMD --load"
elif [[ "$PLATFORMS" == *","* ]]; then
    echo -e "${RED}Error: Multi-platform builds require --push (docker can't load manifest lists locally)${NC}"
    echo -e "Options:"
    echo -e "  1. Push to a registry:  $0 --target $TARGET --push"
    echo -e "  2. Build for one platform locally:  $0 --target $TARGET --load --platform linux/arm64"
    exit 1
else
    BUILD_CMD="$BUILD_CMD --load"
fi

BUILD_CMD="$BUILD_CMD ."

# Execute or show command
echo -e "\n${BLUE}Build command:${NC}"
echo "$BUILD_CMD"
echo ""

if $DRY_RUN; then
    echo -e "${YELLOW}Dry run - command not executed${NC}"
    exit 0
fi

# Execute build
echo -e "${GREEN}Starting build...${NC}\n"
if eval "$BUILD_CMD"; then
    echo -e "\n${GREEN}Build completed successfully!${NC}"

    # Show platform-specific information
    echo -e "\n${BLUE}Platform notes:${NC}"
    echo -e "  ${GREEN}All platforms include camelot-py for table extraction${NC}"
    if [[ "$PLATFORMS" == *"arm64"* ]]; then
        echo -e "  ${YELLOW}ARM64 uses opencv-python-headless (pdftopng not available)${NC}"
    fi

    if $PUSH; then
        echo -e "\n${GREEN}Image pushed to registry${NC}"
        echo -e "Pull with: docker pull $IMAGE_NAME-$TARGET:$TAG"
    elif $LOAD; then
        echo -e "\n${GREEN}Image loaded into local Docker${NC}"
        echo -e "Run with: docker run -p 3030:3030 $IMAGE_NAME-$TARGET:$TAG"
    fi
else
    echo -e "\n${RED}Build failed${NC}"
    exit 1
fi

# Show manifest information if pushed
if $PUSH; then
    echo -e "\n${BLUE}Manifest information:${NC}"
    docker buildx imagetools inspect "$IMAGE_NAME-$TARGET:$TAG" || true
fi
