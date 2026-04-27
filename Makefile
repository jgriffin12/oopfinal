install:
	pip install -r requirements.txt

run:
	python -m apps.main

test:
	pytest -q

coverage:
	pytest --cov=apps --cov-report=term-missing

typecheck:
	mypy apps

style:
	flake8 apps tests

check: style typecheck test coverage