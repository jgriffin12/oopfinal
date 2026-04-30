.RECIPEPREFIX := >
.PHONY: install run test typecheck docs docker-build docker-up docker-down docker-test docker-docs docker-shell clean

install:
> pip install -r requirements.txt

run:
> python -m apps.main

test:
> pytest

typecheck:
> mypy apps

docs:
> pdoc apps -o Docs/pdoc

docker-build:
> docker compose build

docker-up:
> docker compose up --build

docker-down:
> docker compose down

docker-test:
> docker compose run --rm backend pytest

docker-docs:
> docker compose run --rm backend pdoc apps -o Docs/pdoc

docker-shell:
> docker compose run --rm backend bash

clean:
> rm -rf Docs/pdoc .pytest_cache .mypy_cache .coverage htmlcov
> find . -type d -name "__pycache__" -exec rm -rf {} +