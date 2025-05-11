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
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezon

RUN apt upgrade && apt update && apt install -y cron

WORKDIR /code

COPY --from=builder /venv/ venv/
COPY data ./data/bootstrap/
COPY app ./app
COPY --chmod=775 scripts/* ./scripts/

RUN printenv | grep -v "no_proxy" >> /etc/environment && touch /var/log/db_backup.log && crontab scripts/backup_cron

ENTRYPOINT ["./scripts/run.sh"]
