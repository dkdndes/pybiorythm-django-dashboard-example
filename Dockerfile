FROM python:3.12-slim

# Install Git (required for uv to install dependencies from Git repositories)
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user
RUN groupadd -r dashboard && useradd -r -g dashboard dashboard

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache --no-dev

# Copy application code
COPY . .

# Set ownership and switch to non-root user
RUN chown -R dashboard:dashboard /app
USER dashboard

# Run Django setup
RUN uv run python manage.py migrate
RUN uv run python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8002/ || exit 1

EXPOSE 8002

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8002"]