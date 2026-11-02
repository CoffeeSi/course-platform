FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-editable

COPY . .

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /bin/uv /bin/uv

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

EXPOSE 8000

CMD ["sh", "-c", "uv run python manage.py collectstatic --noinput && uv run python manage.py migrate && uv run granian --interface asginl --port 8000 --host 0.0.0.0 config.asgi:application"]