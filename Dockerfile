FROM python:3.10-slim as builder

RUN pip install poetry
RUN mkdir -p /nuts
COPY . /nuts

WORKDIR /nuts
RUN poetry install --without dev

FROM python:3.10-slim as base

COPY --from=builder /nuts /nuts

WORKDIR /nuts
ENV PATH="/nuts/.venv/bin:$PATH"

# line below due to import bug
RUN python3 -c "from napalm.base.exceptions import ConnectionException"

ENTRYPOINT [ "/bin/bash" ]