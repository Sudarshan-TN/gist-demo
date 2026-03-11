# --- Build stage: install dependencies ---
FROM python:3.14.3-alpine3.23 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.10.7 /uv /uvx /bin/

WORKDIR /build

# Venv path must match runtime stage
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy manifests first for layer caching, then install deps
# --no-install-project: only install project dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --compile-bytecode

# Strip metadata, caches, and type stubs (~2-3 MB savings)
RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
    find /app/.venv -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null; \
    find /app/.venv -type f -name "*.pyi" -delete 2>/dev/null; \
    true

# --- Runtime stage: minimal image ---
FROM python:3.14.3-alpine3.23 AS runtime

LABEL org.opencontainers.image.title="list-gists" \
      org.opencontainers.image.description="FastAPI service that lists GitHub gists for a given user" \
      org.opencontainers.image.version="0.1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S -G appgroup -s /sbin/nologin -H appuser

# Remove unused stdlib modules (~3 MB savings)
RUN rm -rf /usr/local/lib/python3.14/ensurepip \
           /usr/local/lib/python3.14/idlelib \
           /usr/local/lib/python3.14/turtle* \
           /usr/local/lib/python3.14/tkinter \
           /usr/local/lib/python3.14/test \
           /usr/local/lib/python3.14/unittest \
           /usr/local/lib/python3.14/pydoc* \
           /usr/local/lib/python3.14/doctest* \
           /usr/local/lib/python3.14/lib2to3

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY gist_api/ ./gist_api/

ENV PATH="/app/.venv/bin:$PATH"

USER appuser
EXPOSE 8080

ENTRYPOINT ["uvicorn"]
CMD ["gist_api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--log-level", "info"]