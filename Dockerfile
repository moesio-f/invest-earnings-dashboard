# Build and install dependencies
FROM python:3.13-slim-bookworm AS builder

COPY requirements.txt ./

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --no-cache-dir -r requirements.txt


# Container for running
FROM python:3.13-slim-bookworm

ENV PATH=/code/venv/bin:$PATH
ENV PYTHONPATH=/code:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY --from=builder /venv/ venv/
COPY app ./app
COPY --chmod=775 scripts/* ./scripts/

ENTRYPOINT ["./scripts/run.sh", "./scripts/run_alembic.sh", "./scripts/start_dashboard.sh"]
