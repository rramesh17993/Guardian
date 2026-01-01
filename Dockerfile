FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

# Export requirements
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/

ENV PYTHONPATH=/app/src

CMD ["kopf", "run", "/app/src/guardian/handlers.py", "--verbose"]
