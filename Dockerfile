# Dockerfile for MechGAIA Green Agent
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY uv.lock ./

# Install uv and dependencies
RUN pip install uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs tasks/level2 tasks/level3

# Set environment variables
ENV PYTHONPATH=/app
ENV AGENTBEATS_HOST=0.0.0.0
ENV AGENTBEATS_PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"AGENTBEATS_PORT\", os.environ.get(\"PORT\", 8080))}/health')" || exit 1

# Run the agent
CMD ["python", "agentbeats_main.py"]
