VENV = venv

ifeq ($(OS),Windows_NT)
    activate_cmd = .\$(VENV)\Scripts\activate
	PYTHON = python
else
	activate_cmd = source $(VENV)/bin/activate
	PYTHON = python3
endif

.PHONY: install
install: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(activate_cmd) && pip install -r requirements.txt


.PHONY: source
source:
	$(activate_cmd)

.PHONY: tests
tests:
	docker compose -f .\tests\test-compose.yml rm -fsv
	docker compose -f ./tests/test-compose.yml up --exit-code-from tests --attach tests --build

.PHONY: lint
lint: source
	$(PYTHON) -m ruff format
	$(PYTHON) -m mypy

.PHONY: fix
fix: source
	$(PYTHON) -m ruff check --fix

.PHONY: clean
clean:
	rm -rf venv
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf __pycache__

.PHONY: dev
dev: source
	uvicorn src.main:app --reload

.PHONY: run
run: source
	uvicorn src.main:app

.PHONY: alembic-revision
alembic-revision: source
	alembic revision --autogenerate
	alembic upgrade head


.PHONY: docker-redis
docker-redis:
	docker compose -f ./docker/redis-compose.yml up -d

.PHONY: docker-mongo
docker-mongo:
	docker compose -f ./docker/mongo-compose.yml up -d

.PHONY: docker-app
docker-app:
	docker compose -f ./docker/app-compose.yml up -d --build

.PHONY: docker-all
docker-all: docker-redis docker-mongo docker-app