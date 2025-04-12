FROM python:3.12.9-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
  default-libmysqlclient-dev \
  python3-dev \
  pkg-config \
  gcc \
  pkg-config \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock .env ./

RUN pip install poetry
RUN poetry install

COPY ddp-api ./

WORKDIR /app/ddp-api
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]