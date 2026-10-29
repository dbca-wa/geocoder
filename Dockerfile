# syntax=docker/dockerfile:1
FROM dhi.io/python:3.15-debian13-dev AS build-stage
LABEL org.opencontainers.image.title="Cadastre Geocoder" \
  org.opencontainers.image.description="DBCA cadastre geocoding service" \
  org.opencontainers.image.source="https://github.com/dbca-wa/geocoder" \
  org.opencontainers.image.vendor="DBCA" \
  org.opencontainers.image.authors="asi@dbca.wa.gov.au"

RUN <<EOF
set -euxo pipefail
apt-get update
apt-get install -y --no-install-recommends \
  gdal-bin \
  proj-bin \
  libgdal36 \
  gcc \
  g++
ldconfig
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOF

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group dev --link-mode=copy --compile-bytecode --no-python-downloads --frozen

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PATH="/app/.venv/bin:$PATH"

COPY geocoder ./geocoder
COPY gunicorn.py entrypoint.sh ./
RUN python -m compileall geocoder

USER nonroot
EXPOSE 8080
# Use entrypoint.sh because we need to single-quote the run command.
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
