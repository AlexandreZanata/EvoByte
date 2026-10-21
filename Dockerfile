# Hermetic, reproducible environment for EvoByte (P159)
FROM python:3.11-slim

# Avoid interactive prompts and bytecode generation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    make \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy dependency specification first for caching
COPY pyproject.toml /workspace/

# Install CPU-only PyTorch and runtime/dev dependencies
RUN pip install --upgrade pip && \
    pip install "torch>=2.2" --index-url https://download.pytorch.org/whl/cpu && \
    pip install "numpy>=1.26" "scipy>=1.11" "sympy>=1.12" "pytest>=8.0" "ruff>=0.4"

# Copy full repository source
COPY . /workspace/

# Install evobyte in editable mode without reinstalling dependencies
RUN pip install --no-deps -e .

# Default command: run verification suite hermetically
CMD ["make", "verify"]
