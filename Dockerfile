FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY config/requirements.txt config/requirements.txt

RUN pip install --no-cache-dir -r config/requirements.txt

COPY config/.env /config/.env

COPY script.py /app

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "echo n | python script.py"]