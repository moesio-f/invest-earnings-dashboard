FROM python:3.13-alpine

# Default port for API
ENV DB_URL=""
ENV NOTIFICATION_QUEUE=""
ENV BROKER_URL=""

WORKDIR /code

COPY ./common common
COPY ./wallet-api/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code to container
COPY ./wallet-api/app app

# Define entrypoint as fastapi run
ENTRYPOINT ["fastapi", "run", "app/api.py", "--host", "0.0.0.0"]
