# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY analyzers/ ./analyzers/
COPY ingestion/ ./ingestion/
COPY pipeline/ ./pipeline/

# Create storage directories
RUN mkdir -p /app/storage/workspace /app/storage/reports /app/storage/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV STORAGE_BASE=/app/storage

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]