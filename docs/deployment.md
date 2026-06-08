# Deployment Guide

This project ships two deliverables:

1. A reproducible **analysis pipeline** that produces `reports/ab_test_results.json` (the statistical read of the experiment).
2. A small **FastAPI prediction service** (`src/ab_testing_ecommerce/api.py`) that loads the trained model artifact (`models/model.joblib`) and serves predictions over HTTP.

## 1. Run the analysis pipeline

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m ab_testing_ecommerce.cli analyze
```

This is a batch step — it writes its result to `reports/ab_test_results.json` and does not need to stay running.

## 2. Train the model artifact

The API needs a trained artifact at `models/model.joblib`. Generate it with:

```bash
PYTHONPATH=src python -m ab_testing_ecommerce.cli train
```

## 3. Serve the prediction API

### Locally

```bash
python -m pip install -r requirements.txt -r requirements-api.txt
PYTHONPATH=src uvicorn ab_testing_ecommerce.api:app --reload
```

The service exposes:

- `GET /health` — liveness check.
- `POST /predict` — batch predictions from a list of JSON records (`{"records": [...]}`).

### With Docker (recommended for reviewers)

The repository includes a `Dockerfile` and `docker-compose.yml` that build the image, install all dependencies and start the API automatically:

```bash
docker compose up --build
```

The API is then available at `http://localhost:8000` (Swagger UI at `http://localhost:8000/docs`). The compose file mounts `models/` and `reports/` read-only into the container, so a freshly trained artifact is picked up on the next restart without rebuilding the image.

To stop the service:

```bash
docker compose down
```

Equivalent `make` targets are available: `make docker-build`, `make docker-up`, `make docker-down`.

## 4. Continuous Integration / Continuous Delivery

`.github/workflows/ci.yml` runs on every push and pull request to `main` and:

1. Installs dependencies and runs the test suite (`pytest`).
2. Builds the Docker image, guaranteeing the container always builds from a clean checkout.

This keeps the deployable artifact (the Docker image) verified on every change, which is the baseline CI/CD setup recommended before promoting a model service to a shared environment.

## 5. Promoting to a cloud environment

Because the service is fully containerized, it can be pushed to any container registry and run on common cloud targets without code changes, for example:

- **Render / Railway / Fly.io**: point the service at the repository; it will detect the `Dockerfile` and build/deploy automatically.
- **AWS ECS / Google Cloud Run / Azure Container Apps**: build and push the image (`docker build -t <registry>/<image>:<tag> .` then `docker push ...`) and create a service from it, exposing port `8000`.

In all cases, make sure a trained `models/model.joblib` is either baked into the image (rebuild after `make train`) or mounted/fetched from object storage at startup.
