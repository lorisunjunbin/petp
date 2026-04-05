FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-nogui.txt /app/requirements-nogui.txt
RUN pip install --no-cache-dir -r /app/requirements-nogui.txt

COPY . /app

EXPOSE 8866

CMD ["python", "PETP_backgroud.py"]


