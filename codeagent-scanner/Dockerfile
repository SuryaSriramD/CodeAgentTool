# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.12-slim-bookworm
FROM ${PYTHON_IMAGE} AS runtime-dependencies
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app STORAGE_BASE=/data
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 codeagent \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin codeagent
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt
RUN mkdir -p /data/uploads /data/snapshots /data/reports /data/reviews /data/tmp /var/cache/trivy \
    && chown -R 10001:10001 /data /var/cache/trivy
USER 10001:10001

FROM runtime-dependencies AS api-base
COPY api/ ./api/
COPY analyzers/ ./analyzers/
COPY ingestion/ ./ingestion/
COPY integration/ ./integration/
COPY pipeline/ ./pipeline/
COPY rules/ ./rules/
COPY dotnet-analyzer/ ./dotnet-analyzer/
COPY settings.py worker.py run.py cli.py ./

FROM api-base AS api
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]

FROM mcr.microsoft.com/dotnet/sdk:10.0.401 AS dotnet-build
WORKDIR /src
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
COPY dotnet-analyzer/ ./
RUN dotnet restore CodeAgent.DotNet.fsproj --locked-mode \
    && dotnet publish CodeAgent.DotNet.fsproj -c Release --no-restore -o /publish

FROM mcr.microsoft.com/dotnet/runtime:10.0 AS dotnet-runtime
FROM aquasec/trivy:0.74.0 AS trivy

FROM runtime-dependencies AS scanner
USER root
RUN apt-get update && apt-get install -y --no-install-recommends libicu72 libssl3 libstdc++6 zlib1g \
    && rm -rf /var/lib/apt/lists/*
# Tool dependencies are isolated from the API's Pydantic/OpenAI graph.
COPY requirements-tools.txt /tmp/requirements-tools.txt
RUN python -m venv /opt/scanner-tools \
    && /opt/scanner-tools/bin/pip install --no-cache-dir --require-hashes -r /tmp/requirements-tools.txt \
    && ln -s /opt/scanner-tools/bin/semgrep /usr/local/bin/semgrep \
    && ln -s /opt/scanner-tools/bin/bandit /usr/local/bin/bandit
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY --from=dotnet-runtime /usr/share/dotnet /usr/share/dotnet
COPY --from=dotnet-build /publish /opt/codeagent-dotnet-analyzer
RUN ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet
COPY --from=api-base /app /app
ENV DOTNET_ROOT=/usr/share/dotnet DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
    CODEAGENT_DOTNET_ANALYZER=/opt/codeagent-dotnet-analyzer/CodeAgent.DotNet.dll \
    TRIVY_CACHE_DIR=/var/cache/trivy SNAPSHOT_ROOT=/data/snapshots \
    SEMGREP_SEND_METRICS=off SEMGREP_ENABLE_VERSION_CHECK=0
USER 10001:10001
EXPOSE 8090
CMD ["python", "-m", "uvicorn", "api.scanner:app", "--host", "0.0.0.0", "--port", "8090"]

FROM scanner AS scanner-test
USER root
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements-dev.txt
COPY tests/ ./tests/
COPY fixtures/ ./fixtures/
COPY evaluation/ ./evaluation/
USER 10001:10001
ENV PYTEST_ADDOPTS="-o cache_dir=/tmp/pytest-cache -o asyncio_mode=auto"
CMD ["python", "-m", "pytest", "-q", "tests"]
