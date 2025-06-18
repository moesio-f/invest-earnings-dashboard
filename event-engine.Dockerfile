FROM python:3.13-alpine AS base

ENV BROKER_URL="amqp://guest:guest@broker:5672/?heartbeat=30"

WORKDIR /code

COPY ./common common
COPY ./event-engine/engine engine
COPY ./event-engine/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    pip install --no-cache-dir -r requirements.txt

# Define entrypoint as python
ENTRYPOINT ["python", "-m"]


# Router
FROM base AS router
ENV NOTIFICATION_QUEUE="notification.router.queue"
ENV YOC_QUEUE="processor.yoc.queue"

CMD ["engine.router"]

#  YoC processor
FROM base AS yoc-processor
ENV YOC_QUEUE="processor.yoc.queue"
ENV WALLET_DB_URL=""
ENV ANALYTIC_DB_URL=""

CMD ["engine.processors.yoc"]
