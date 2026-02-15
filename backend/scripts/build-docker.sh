#!/bin/bash
# Enhanced Docker Build Script for Financial Data Extractor
#
# Features:
# - Parallel builds for faster execution
# - Build caching with BuildKit
# - Security scanning with Trivy
# - Image size reporting
# - Multi-platform support
# - SBOM generation
#
# Usage:
#   ./scripts/build-docker.sh [api|worker|all] [OPTIONS]
#
# Options:
#   --push                  Push images to registry after building
#   --registry=REGISTRY     Registry URL (e.g., ghcr.io/your-org)
#   --scan                  Run security scan with Trivy
#   --parallel              Build images in parallel (default: sequential)
#   --platform=PLATFORM     Target platform (e.g., linux/amd64,linux/arm64)
#   --no-cache              Build without using cache
#   --sbom                  Generate Software Bill of Materials
#   --compress              Compress final images
#   --help, -h             Show this help message
#
# Examples:
#   ./scripts/build-docker.sh all
#   ./scripts/build-docker.sh all --push --registry=ghcr.io/your-org --scan
#   ./scripts/build-docker.sh api --platform=linux/amd64,linux/arm64
#   ./scripts/build-docker.sh worker --parallel --sbom

set -euo pipefail

# ============================================================================
# Configuration and Colors
# ============================================================================
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_GREEN='\033[32m'
COLOR_YELLOW='\033[33m'
COLOR_BLUE='\033[34m'
COLOR_RED='\033[31m'
COLOR_CYAN='\033[36m'

# Default values
IMAGE_TYPE="all"
PUSH=false
REGISTRY=""
SCAN=false
PARALLEL=false
PLATFORM="linux/amd64"
NO_CACHE=false
SBOM=false
COMPRESS=false
IMAGE_NAME="financial-data-extractor"

# Get version from pyproject.toml
VERSION=$(grep '^version' pyproject.toml 2>/dev/null | cut -d '"' -f 2 || echo "latest")
IMAGE_TAG="${VERSION}"
IMAGE_TAG_LATEST="latest"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# ============================================================================
# Helper Functions
# ============================================================================
log_info() {
    echo -e "${COLOR_BLUE}ℹ️  $1${COLOR_RESET}"
}

log_success() {
    echo -e "${COLOR_GREEN}✅ $1${COLOR_RESET}"
}

log_warning() {
    echo -e "${COLOR_YELLOW}⚠️  $1${COLOR_RESET}"
}

log_error() {
    echo -e "${COLOR_RED}❌ $1${COLOR_RESET}"
}

log_header() {
    echo -e "${COLOR_BOLD}${COLOR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
    echo -e "${COLOR_BOLD}${COLOR_CYAN}$1${COLOR_RESET}"
    echo -e "${COLOR_BOLD}${COLOR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
}

# Check if required tools are installed
check_requirements() {
    local missing_tools=()

    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if [[ "$SCAN" == true ]] && ! command -v trivy &> /dev/null; then
        log_warning "Trivy not found. Install it from: https://github.com/aquasecurity/trivy"
        log_warning "Skipping security scan..."
        SCAN=false
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi

    # Check Docker BuildKit support
    if ! docker buildx version &> /dev/null; then
        log_warning "Docker BuildKit not available. Some features may not work."
    fi
}

# Get image size
get_image_size() {
    local image=$1
    docker images --format "{{.Size}}" "$image" | head -n 1
}

# Run security scan with Trivy
run_security_scan() {
    local image=$1
    local image_name=$2

    log_header "Running Security Scan: $image_name"

    if command -v trivy &> /dev/null; then
        trivy image --severity HIGH,CRITICAL "$image" || true
        log_success "Security scan completed for $image_name"
    else
        log_warning "Trivy not installed, skipping security scan"
    fi
}

# Generate SBOM
generate_sbom() {
    local image=$1
    local image_name=$2
    local output_file="sbom-${image_name}-${IMAGE_TAG}.json"

    log_info "Generating SBOM for $image_name..."

    if docker buildx imagetools inspect "$image" --format '{{json .SBOM}}' > "$output_file" 2>/dev/null; then
        log_success "SBOM generated: $output_file"
    else
        log_warning "Could not generate SBOM (requires BuildKit SBOM support)"
    fi
}

# ============================================================================
# Build Function
# ============================================================================
build_image() {
    local image_name=$1
    local full_image_name="${IMAGE_NAME}-${image_name}"

    log_header "Building ${image_name} Image"
    log_info "Image: ${full_image_name}:${IMAGE_TAG}"
    log_info "Target: ${image_name}"
    log_info "Platform: ${PLATFORM}"

    if [ -n "${REGISTRY}" ]; then
        log_info "Registry: ${REGISTRY}/${full_image_name}:${IMAGE_TAG}"
    fi

    # Build command with BuildKit
    local build_cmd="docker buildx build"

    # Add platform support
    build_cmd="${build_cmd} --platform ${PLATFORM}"

    # Add build args
    build_cmd="${build_cmd} --build-arg BUILD_DATE=${BUILD_DATE}"
    build_cmd="${build_cmd} --build-arg VCS_REF=${VCS_REF}"
    build_cmd="${build_cmd} --build-arg VERSION=${VERSION}"

    # Add image-specific build args
    if [ "${image_name}" = "api" ]; then
        build_cmd="${build_cmd} --build-arg API_PORT=3030"
    elif [ "${image_name}" = "worker" ]; then
        build_cmd="${build_cmd} --build-arg CELERY_CONCURRENCY=4"
        build_cmd="${build_cmd} --build-arg CELERY_MAX_TASKS_PER_CHILD=1000"
    fi

    # Add cache options
    if [ "${NO_CACHE}" = false ]; then
        build_cmd="${build_cmd} --cache-from type=local,src=/tmp/.buildx-cache"
        build_cmd="${build_cmd} --cache-to type=local,dest=/tmp/.buildx-cache-new,mode=max"
    else
        build_cmd="${build_cmd} --no-cache"
    fi

    # Add SBOM generation
    if [ "${SBOM}" = true ]; then
        build_cmd="${build_cmd} --sbom=true"
    fi

    # Add provenance (only for push builds; --load can't handle manifest lists)
    if [ "${PUSH}" = true ] && [ -n "${REGISTRY}" ]; then
        build_cmd="${build_cmd} --provenance=true"
    else
        build_cmd="${build_cmd} --provenance=false"
    fi

    # Add compression
    if [ "${COMPRESS}" = true ]; then
        build_cmd="${build_cmd} --compress"
    fi

    # Add target and Dockerfile
    build_cmd="${build_cmd} --target ${image_name}"
    build_cmd="${build_cmd} -f Dockerfile"
    build_cmd="${build_cmd} -t ${full_image_name}:${IMAGE_TAG}"
    build_cmd="${build_cmd} -t ${full_image_name}:${IMAGE_TAG_LATEST}"

    # Add registry tags if specified
    if [ -n "${REGISTRY}" ]; then
        build_cmd="${build_cmd} -t ${REGISTRY}/${full_image_name}:${IMAGE_TAG}"
        build_cmd="${build_cmd} -t ${REGISTRY}/${full_image_name}:${IMAGE_TAG_LATEST}"
    fi

    # Add load flag for single platform or push flag
    if [[ "${PLATFORM}" == *","* ]]; then
        if [ "${PUSH}" = true ] && [ -n "${REGISTRY}" ]; then
            build_cmd="${build_cmd} --push"
        else
            log_warning "Multi-platform build without push - images won't be available locally"
        fi
    else
        build_cmd="${build_cmd} --load"
    fi

    # Add context
    build_cmd="${build_cmd} ."

    # Execute build
    log_info "Executing: ${build_cmd}"
    if eval "${build_cmd}"; then
        log_success "${image_name} image built successfully!"

        # Rotate cache
        if [ "${NO_CACHE}" = false ] && [ -d "/tmp/.buildx-cache-new" ]; then
            rm -rf /tmp/.buildx-cache
            mv /tmp/.buildx-cache-new /tmp/.buildx-cache
        fi

        # Show image size (only for single-platform builds that are loaded)
        if [[ "${PLATFORM}" != *","* ]]; then
            local image_size=$(get_image_size "${full_image_name}:${IMAGE_TAG}")
            log_info "Image size: ${image_size}"
        fi

        # Run security scan
        if [ "${SCAN}" = true ]; then
            run_security_scan "${full_image_name}:${IMAGE_TAG}" "${image_name}"
        fi

        # Push images
        if [ "${PUSH}" = true ]; then
            if [ -z "${REGISTRY}" ]; then
                log_warning "Push requested but no registry provided. Skipping push."
            elif [[ "${PLATFORM}" != *","* ]]; then
                # For single-platform builds, push manually
                log_info "Pushing ${image_name} to ${REGISTRY}..."
                docker push "${REGISTRY}/${full_image_name}:${IMAGE_TAG}"
                docker push "${REGISTRY}/${full_image_name}:${IMAGE_TAG_LATEST}"
                log_success "${image_name} pushed successfully!"
            fi
        fi

        # Generate SBOM
        if [ "${SBOM}" = true ] && [ -n "${REGISTRY}" ]; then
            generate_sbom "${REGISTRY}/${full_image_name}:${IMAGE_TAG}" "${image_name}"
        fi

        return 0
    else
        log_error "Failed to build ${image_name} image"
        return 1
    fi
}

# Build function wrapper for parallel execution
build_image_parallel() {
    build_image "$@" &
}

# ============================================================================
# Argument Parsing
# ============================================================================
show_help() {
    cat << EOF
${COLOR_BOLD}Docker Image Builder for Financial Data Extractor${COLOR_RESET}

${COLOR_BOLD}Usage:${COLOR_RESET}
  $0 [api|worker|all] [OPTIONS]

${COLOR_BOLD}Image Types:${COLOR_RESET}
  api              Build FastAPI image only
  worker           Build Celery worker image only
  all              Build all images (default)

${COLOR_BOLD}Options:${COLOR_RESET}
  --push                  Push images to registry after building
  --registry=REG          Registry URL (e.g., ghcr.io/your-org)
  --scan                  Run security scan with Trivy
  --parallel              Build images in parallel
  --platform=PLATFORM     Target platform (e.g., linux/amd64,linux/arm64)
  --no-cache              Build without using cache
  --sbom                  Generate Software Bill of Materials
  --compress              Compress final images
  --help, -h             Show this help message

${COLOR_BOLD}Examples:${COLOR_RESET}
  $0 all
  $0 all --push --registry=ghcr.io/your-org
  $0 api --scan --sbom
  $0 worker --platform=linux/amd64,linux/arm64 --push --registry=ghcr.io/your-org
  $0 all --parallel --no-cache

${COLOR_BOLD}Environment Variables:${COLOR_RESET}
  DOCKER_REGISTRY         Default registry (overridden by --registry)
  DOCKER_BUILDKIT         Enable BuildKit (set to 1)

EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        api|worker|all)
            IMAGE_TYPE="$1"
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --registry=*)
            REGISTRY="${1#*=}"
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --scan)
            SCAN=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --platform=*)
            PLATFORM="${1#*=}"
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --sbom)
            SBOM=true
            shift
            ;;
        --compress)
            COMPRESS=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# Main Execution
# ============================================================================
cd "$(dirname "$0")/.." || exit 1

# Enable BuildKit
export DOCKER_BUILDKIT=1

# Check requirements
check_requirements

# Print build information
log_header "Docker Image Builder"
echo "Version: ${VERSION}"
echo "Build Date: ${BUILD_DATE}"
echo "VCS Ref: ${VCS_REF}"
echo "Platform(s): ${PLATFORM}"
echo "Parallel: ${PARALLEL}"
echo "Security Scan: ${SCAN}"
echo "SBOM Generation: ${SBOM}"
echo ""

# Create buildx builder if it doesn't exist
if ! docker buildx inspect multiplatform &> /dev/null; then
    log_info "Creating buildx builder instance..."
    docker buildx create --name multiplatform --use
    docker buildx inspect --bootstrap
fi

# Execute builds
case "${IMAGE_TYPE}" in
    api)
        build_image "api"
        ;;
    worker)
        build_image "worker"
        ;;
    all)
        if [ "${PARALLEL}" = true ]; then
            log_info "Building images in parallel..."
            build_image_parallel "api"
            build_image_parallel "worker"
            wait
        else
            build_image "api"
            echo ""
            build_image "worker"
        fi
        ;;
    *)
        log_error "Invalid image type: ${IMAGE_TYPE}"
        echo "Use: api, worker, or all"
        exit 1
        ;;
esac

# Print summary
echo ""
log_header "Build Summary"
log_success "All builds completed successfully!"
echo ""
log_info "Built images:"
echo "  • ${IMAGE_NAME}-api:${IMAGE_TAG}"
echo "  • ${IMAGE_NAME}-worker:${IMAGE_TAG}"

if [ -n "${REGISTRY}" ] && [ "${PUSH}" = true ]; then
    echo ""
    log_info "Images pushed to registry:"
    echo "  • ${REGISTRY}/${IMAGE_NAME}-api:${IMAGE_TAG}"
    echo "  • ${REGISTRY}/${IMAGE_NAME}-worker:${IMAGE_TAG}"
fi

log_success "Done! 🎉"
