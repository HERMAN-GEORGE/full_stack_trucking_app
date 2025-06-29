
FROM python:3.9-slim-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=120 -r requirements.txt # <--- CHANGE THIS LINE: Increased timeout to 120 seconds


COPY . /app/


EXPOSE 9090
CMD ["python", "manage.py", "runserver", "0.0.0.0:9090"]