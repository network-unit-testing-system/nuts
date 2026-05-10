FROM python:3.13-slim

WORKDIR /workspace

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

ENV UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --frozen --no-cache --all-extras

# line below due to import bug
RUN python3 -c "from napalm.base.exceptions import ConnectionException"

ENTRYPOINT [ "/bin/bash" ]