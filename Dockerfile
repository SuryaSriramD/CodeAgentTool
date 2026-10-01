# API-only compatibility build: docker build -t codeagent-api:local .
# Use docker compose up --build for API/worker/scanner/UI.
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app STORAGE_BASE=/data
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 codeagent \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin codeagent
COPY codeagent-scanner/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt
COPY codeagent-scanner/api/ ./api/
COPY codeagent-scanner/analyzers/ ./analyzers/
COPY codeagent-scanner/ingestion/ ./ingestion/
COPY codeagent-scanner/integration/ ./integration/
COPY codeagent-scanner/pipeline/ ./pipeline/
COPY codeagent-scanner/rules/ ./rules/
COPY codeagent-scanner/dotnet-analyzer/ ./dotnet-analyzer/
COPY codeagent-scanner/settings.py codeagent-scanner/worker.py codeagent-scanner/run.py codeagent-scanner/cli.py ./
RUN mkdir -p /data/uploads /data/snapshots /data/reports /data/reviews /data/tmp \
    && chown -R 10001:10001 /data
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
