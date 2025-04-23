FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
ENV UV_COMPILE_BYTECODE=1
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"


ENV PYTHONUNBUFFERED=1

WORKDIR /aggregator
COPY uv.lock pyproject.toml ./
RUN uv sync --locked

COPY ./ ./
