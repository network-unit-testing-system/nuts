FROM python:3.10-slim as builder

RUN pip install poetry
RUN mkdir -p /app
COPY . /app

WORKDIR /app

RUN python3 -m venv .venv && poetry install --without dev

FROM python:3.10-slim as base

COPY --from=builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# line below due to import bug
RUN python3 -c "from napalm.base.exceptions import ConnectionException"

ENTRYPOINT [ "/bin/bash" ]