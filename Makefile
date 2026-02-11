test:
	poetry run pytest tests

install:
	poetry install

build: install
	poetry run pip freeze --exclude-editable > requirements.txt
	docker build -t bagoftricks:latest .

run:
	poetry run python wsgi.py