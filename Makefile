test:
	poetry run pytest tests

install:
	poetry install

install-dev:
	poetry install --with dev

build: install
	poetry run pip freeze --exclude-editable > requirements.txt
	poetry build
	docker build -t bagoftricks\:latest .

test-docker: build
	docker run -p 5000:5000 -e SESSION_COOKIE_NAME="SESSION_COOKIE_NAME" -e SECRET_KEY="SECRET_KEY" bagoftricks:latest

install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

run:
	poetry run python wsgi.py