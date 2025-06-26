FROM python:3.13-alpine

ENV DB_URL=""
ENV NOTIFICATION_QUEUE=""
ENV BROKER_URL=""
ENV PYTHONPATH="/code/app"
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./common/invest_earning common/invest_earning
COPY ./common/pyproject.toml common/pyproject.toml
COPY ./market-scrappers/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    pip install --no-cache-dir -r requirements.txt && \
    apk add --no-cache tzdata

# Copy source code to container
COPY ./market-scrappers app

CMD ["./app/scripts/run_blocking.sh"]
