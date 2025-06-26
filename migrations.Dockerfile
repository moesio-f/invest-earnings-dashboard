FROM python:3.13-alpine

ENV WALLET_DB_URL=""
ENV ANALYTIC_DB_URL=""
ENV BOOTSTRAP_DATA_PATH="/code/boostrap/"
ENV BACKUP_DUMP_PATH="/code/backup/"

WORKDIR /code

COPY ./common common

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    apk add --no-cache tzdata

CMD ["./common/scripts/run_migrations.sh"]

