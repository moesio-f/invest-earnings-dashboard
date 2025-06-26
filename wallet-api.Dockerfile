FROM python:3.13-alpine

ENV DB_URL=""
ENV NOTIFICATION_QUEUE=""
ENV BROKER_URL=""

WORKDIR /code

COPY ./common/invest_earning common/invest_earning
COPY ./common/pyproject.toml common/pyproject.toml
COPY ./wallet-api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    pip install --no-cache-dir -r requirements.txt && \
    apk add --no-cache tzdata

# Copy source code to container
COPY ./wallet-api/app app

# Define entrypoint as fastapi run
ENTRYPOINT ["fastapi", "run", "app/api.py", "--host", "0.0.0.0"]
