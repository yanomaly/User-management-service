FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.7.1

WORKDIR /app

RUN pip install --ignore-installed "poetry==$POETRY_VERSION"

COPY ../poetry.lock pyproject.toml /app/
RUN poetry export --without-hashes --format requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

COPY . /app/

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
