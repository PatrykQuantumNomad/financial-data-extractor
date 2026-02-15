# Multi-stage Dockerfile for FastAPI API server and Celery worker
# Uses SERVICE build arg to select the runtime target
#
# Build API:    docker build --build-arg SERVICE=api -t app-api .
# Build Worker: docker build --build-arg SERVICE=worker -t app-worker .

# ============================================================================
# Stage 1: Builder - Install dependencies with platform-aware handling
# ============================================================================
FROM python:3.13-slim AS builder

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
# Docker automatically provides these during buildx builds
ARG TARGETARCH
ARG TARGETOS

RUN echo "Building for: ${TARGETOS}/${TARGETARCH}"

# Install system dependencies required for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv==0.5.0

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md* ./

# ============================================================================
# Dependency Installation
# ============================================================================
# camelot-py[base] is removed from pyproject.toml before uv sync because:
#   - Its [base] extra pulls opencv-python (needs libGL) and pdftopng (no ARM64 wheels)
#   - Instead we install camelot-py + ghostscript + opencv-python-headless separately
#   - opencv-python-headless is lighter and works on all architectures
#   - On AMD64 we also add pdftopng; on ARM64 we skip it (no wheels available)

RUN python3 << 'PATCH_DEPS'
import os

with open('pyproject.toml', 'r') as f:
    lines = f.readlines()

with open('pyproject.toml', 'w') as f:
    for line in lines:
        if '"camelot-py' in line or "'camelot-py" in line:
            print(f"  Removed from pyproject.toml: {line.strip()}")
            print(f"  (will be installed separately with headless opencv)")
            continue
        f.write(line)
PATCH_DEPS

# Install core dependencies (without camelot-py[base])
# --frozen will fail since pyproject.toml was modified; fall back to re-resolve
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen || \
    (echo "Lock file mismatch after patching pyproject.toml, re-resolving..." && uv sync --no-dev)

RUN test -d /app/.venv || (echo "Virtual environment not created!" && exit 1)

# ============================================================================
# Install camelot-py with headless opencv (all architectures)
# ============================================================================
# ghostscript: pure Python, works everywhere
# opencv-python-headless: has wheels for both AMD64 and ARM64, no libGL needed
# pdftopng: only has AMD64 Linux wheels, skip on ARM

RUN uv pip install --python /app/.venv/bin/python --no-cache \
        'camelot-py>=0.11.0,<0.12.0' \
        ghostscript \
        opencv-python-headless && \
    if [ "$TARGETARCH" != "arm64" ] && [ "$TARGETARCH" != "arm" ]; then \
        echo "Installing pdftopng for ${TARGETARCH}..." && \
        uv pip install --python /app/.venv/bin/python --no-cache pdftopng || \
        echo "pdftopng not available (non-critical)" ; \
    else \
        echo "Skipping pdftopng on ARM (no wheels available)" ; \
    fi

# ============================================================================
# Verification - ensure critical packages can be imported
# ============================================================================
RUN /app/.venv/bin/python3 << 'VERIFY'
import sys, importlib.util, os

def check(name):
    try:
        spec = importlib.util.find_spec(name)
        if spec is not None:
            __import__(name)
            return True, "OK"
        return False, "Not found"
    except Exception as e:
        return False, str(e)

critical = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'asyncpg',
            'celery', 'redis']
optional = ['camelot', 'PIL', 'cv2']

print("=" * 50)
print("Package Verification")
print("=" * 50)

failed = []
for pkg in critical:
    ok, msg = check(pkg)
    print(f"  {'OK' if ok else 'FAIL':5s} {pkg:20s} {msg}")
    if not ok:
        failed.append(pkg)

print()
for pkg in optional:
    ok, msg = check(pkg)
    print(f"  {'OK' if ok else 'skip':5s} {pkg:20s} {msg}")

if failed:
    print(f"\nCRITICAL: Failed to import: {', '.join(failed)}")
    sys.exit(1)

arch = os.environ.get('TARGETARCH', 'unknown')
camelot_ok, _ = check('camelot')
if not camelot_ok:
    print(f"\nWARNING: camelot not available on {arch} - table extraction will use pdfplumber fallback")
else:
    print(f"\nAll packages verified (including camelot on {arch})")
print("=" * 50)
VERIFY


# ============================================================================
# Stage 2: Runtime base (shared between API and worker)
# ============================================================================
FROM python:3.13-slim AS runtime-base

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG TARGETARCH
ARG TARGETOS

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libpq5 \
    libjpeg62-turbo \
    libpng16-16 \
    libtiff6 \
    libwebp7 \
    ghostscript \
    curl \
    ca-certificates \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with home directory (crawl4ai needs a writable home)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

WORKDIR /app

# Copy Python virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Environment configuration
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser config.py ./

# Build info for debugging
RUN echo "Built for: ${TARGETOS}/${TARGETARCH}" > /app/build_info.txt && \
    echo "Build date: ${BUILD_DATE}" >> /app/build_info.txt && \
    echo "Version: ${VERSION}" >> /app/build_info.txt && \
    chown appuser:appuser /app/build_info.txt


# ============================================================================
# Stage 3a: FastAPI API server
# ============================================================================
FROM runtime-base AS api

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG API_PORT=3030
ARG TARGETARCH
ARG TARGETOS

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/PatrykQuantumNomad/financial-data-extractor" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="PatrykQuantumNomad" \
      org.opencontainers.image.title="Financial Data Extractor API" \
      org.opencontainers.image.description="FastAPI service for financial data extraction" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.architecture="${TARGETARCH}" \
      org.opencontainers.image.os="${TARGETOS}"

# Copy API-specific files
COPY --chown=appuser:appuser run.py ./
COPY --chown=appuser:appuser logging.json ./
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic/ ./alembic/

ENV API_PORT=${API_PORT}

USER appuser

EXPOSE ${API_PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/healthcheck || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["uvicorn", "run:application", \
     "--host", "0.0.0.0", \
     "--port", "3030", \
     "--log-level", "info", \
     "--no-access-log"]


# ============================================================================
# Stage 3b: Celery worker
# ============================================================================
FROM runtime-base AS worker

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG CELERY_CONCURRENCY=4
ARG CELERY_MAX_TASKS_PER_CHILD=1000
ARG TARGETARCH
ARG TARGETOS

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="https://github.com/PatrykQuantumNomad/financial-data-extractor" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="PatrykQuantumNomad" \
      org.opencontainers.image.title="Financial Data Extractor Worker" \
      org.opencontainers.image.description="Celery worker for financial data extraction tasks" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.architecture="${TARGETARCH}" \
      org.opencontainers.image.os="${TARGETOS}"

# Worker needs procps for health checks + playwright browser deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    # Playwright/Chromium dependencies
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 \
    libxshmfence1 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

ENV CELERY_BROKER_URL="" \
    CELERY_RESULT_BACKEND="" \
    CELERY_CONCURRENCY=${CELERY_CONCURRENCY} \
    CELERY_MAX_TASKS_PER_CHILD=${CELERY_MAX_TASKS_PER_CHILD} \
    C_FORCE_ROOT="false" \
    CELERY_TASK_ACKS_LATE="true" \
    CELERY_WORKER_PREFETCH_MULTIPLIER="1"

# Install Playwright Chromium browser to a fixed path accessible by appuser
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
RUN /app/.venv/bin/playwright install --with-deps chromium \
    && chmod -R o+rx /opt/playwright-browsers

# Create directory for Celery worker state
RUN mkdir -p /tmp/celery && chown appuser:appuser /tmp/celery

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD celery -A app.tasks.celery_app inspect ping -d "celery@${HOSTNAME}" -t 5 || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["sh", "-c", "celery -A app.tasks.celery_app worker \
    --loglevel=info \
    -Q scraping,extraction,compilation,orchestration,default \
    --concurrency=${CELERY_CONCURRENCY} \
    --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD} \
    --time-limit=300 \
    --soft-time-limit=240 \
    -O fair \
    --without-gossip \
    --without-mingle \
    --without-heartbeat"]
