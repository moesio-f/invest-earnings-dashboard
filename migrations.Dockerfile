FROM python:3.13-alpine

ENV WALLET_DB_URL=""
ENV ANALYTIC_DB_URL=""
ENV BOOTSTRAP_DATA_PATH="/code/data/"

WORKDIR /code

COPY ./common common

# Install dependencies
RUN pip install --no-cache-dir ./common


ENTRYPOINT ["./common/scripts/run_migrations.sh"]

