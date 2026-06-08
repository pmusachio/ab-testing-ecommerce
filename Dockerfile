FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

COPY requirements.txt requirements-api.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

COPY configs ./configs
COPY src ./src
COPY models ./models

EXPOSE 8000

CMD ["uvicorn", "ab_testing_ecommerce.api:app", "--host", "0.0.0.0", "--port", "8000"]
