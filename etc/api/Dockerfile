FROM python:3.9.7-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    VENV_PATH=/opt/venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS poetry
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    libcurl4-openssl-dev libssl-dev && \
    pip install pip==21.2.4 && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && mv /root/.poetry $POETRY_PATH \
    && poetry --version \
    \
    && python -m venv $VENV_PATH \
    && poetry config virtualenvs.create false \
    \
    && rm -rf /var/lib/apt/lists/*

FROM poetry AS build-short_url

WORKDIR /app/

COPY ./src/pyproject.toml ./src/poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root

FROM build-short_url AS develop

COPY ./src /app

CMD ["python", "short_url", "serve"]
