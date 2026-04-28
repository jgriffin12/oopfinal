.RECIPEPREFIX := >
.PHONY: install run test typecheck docker-build docker-up docker-down docker-test docker-shell

install:
> pip install -r requirements.txt

run:
> python -m apps.main

test:
> pytest

typecheck:
> mypy apps

docker-build:
> docker compose build

docker-up:
> docker compose up --build

docker-down:
> docker compose down

docker-test:
> docker compose run --rm backend pytest

docker-shell:
> docker compose run --rm backend bash
