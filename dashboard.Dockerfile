FROM python:3.13-alpine

ENV WALLET_API_URL=""
ENV BROKER_URL=""

WORKDIR /code

COPY ./common/invest_earning common/invest_earning
COPY ./common/pyproject.toml common/pyproject.toml
COPY ./dashboard/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir ./common && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code to container
COPY ./dashboard/app app

ENTRYPOINT ["python", "-m", "streamlit", "run", "app/entrypoint.py"]
