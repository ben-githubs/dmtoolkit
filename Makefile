test:
	poetry run pytest tests

install:
	poetry install

install-dev:
	poetry install --with dev

build: install
	poetry run pip freeze --exclude-editable > requirements.txt
	docker build -t bagoftricks:latest .


install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

run:
	poetry run python wsgi.py