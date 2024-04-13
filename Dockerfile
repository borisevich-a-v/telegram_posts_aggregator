FROM python:3.11-bookworm

RUN apt-get update -y  \
    && python -m pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . .
CMD poetry run python src/__main__.py
