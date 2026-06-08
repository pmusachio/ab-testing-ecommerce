.PHONY: install profile train analyze test api docker-build docker-up docker-down

install:
	python -m pip install -r requirements.txt -r requirements-api.txt

profile:
	PYTHONPATH=src python -m ab_testing_ecommerce.cli profile

train:
	PYTHONPATH=src python -m ab_testing_ecommerce.cli train

analyze:
	PYTHONPATH=src python -m ab_testing_ecommerce.cli analyze

test:
	python -m pytest

api:
	PYTHONPATH=src uvicorn ab_testing_ecommerce.api:app --reload

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
