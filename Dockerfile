# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
# --frozen: strict version matching using lockfile (if we had one, but we'll use install for now as it's fresh)
# --no-dev: do not install dev dependencies
RUN uv pip install --system -r <(uv pip compile pyproject.toml)

# Copy source code
COPY . .

# Expose the server port
EXPOSE 3333

# Run the server
CMD ["python", "-m", "src.server"]
