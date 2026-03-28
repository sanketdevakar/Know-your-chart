FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Do not run as root — create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV PORT=8080
ENV MCP_PORT=8081

# 8081 — internal MCP server
# 8080 — FastAPI agent (Cloud Run maps $PORT to this)
EXPOSE 8080 8081

# Health check — Cloud Run uses this to verify the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Start MCP server in background, wait for it to be ready,
# then start the FastAPI agent
# Cloud Run injects $PORT automatically — defaults to 8080 locally
CMD ["sh", "-c", \
     "python mcp_server/server.py & \
      sleep 3 && \
      uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]