# Building stage
FROM python:3.10-buster as builder

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock /app/
RUN pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --only main \
  && rm -rf ~/.cache

# Running stage
FROM python:3.10-slim-buster as runner

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

RUN groupadd -r app \
  && useradd -r -g app app
WORKDIR /app
COPY ./src/ /app/
COPY --chown=app:app . ./
USER app

CMD exec gunicorn --bind :$PORT --log-level info --workers 1 --threads 8 --timeout 0 app:app
