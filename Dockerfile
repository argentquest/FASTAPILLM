# Multi-stage Docker build for AI Content Generation Platform

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs && \
    chown -R appuser:appuser /app

# Make sure scripts are executable
RUN chmod +x /app/backend/main.py

# Set Python path
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Metadata labels
LABEL maintainer="AI Content Platform Team" \
      version="1.0.0" \
      description="AI Content Generation Platform with multi-framework support" \
      org.opencontainers.image.title="AI Content Generation Platform" \
      org.opencontainers.image.description="Modern AI content generation platform with Semantic Kernel, LangChain, and LangGraph support" \
      org.opencontainers.image.vendor="AI Content Platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.schema-version="1.0"