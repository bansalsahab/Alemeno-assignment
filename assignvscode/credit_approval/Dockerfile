# Dockerfile for Django + Celery + Gunicorn
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

COPY start.sh /start.sh
RUN chmod +x /start.sh
ENV PYTHONPATH=/app/app
CMD ["/start.sh"]
