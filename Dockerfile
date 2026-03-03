FROM python:3.11-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY dmtoolkit dmtoolkit
COPY config.py wsgi.py pyproject.toml dist README.md ./

RUN pip install -e .

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]