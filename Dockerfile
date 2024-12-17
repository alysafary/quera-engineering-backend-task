FROM python:3.12-slim AS image-base

#curl: for downloading poetry install script
ARG APT_BUILDER="curl"

# Common Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYSETUP_PATH="/pysetup" \
    POETRY_HOME="/poetry" \
    POETRY_VERSION=1.6.1 \
    # https://stackoverflow.com/a/74784239/1744633
    POETRY_INSTALLER_MAX_WORKERS=10 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR="/var/cache/pypoetry" \
    PIP_CACHE_DIR="/var/cache/pip"


##################################################### Builder Base #####################################################
FROM image-base AS builder-base

RUN apt-get update && apt-get install --no-install-recommends -y $APT_BUILDER

# Install Poetry
# Respects $POETRY_VERSION and $POETRY_HOME
# The installer uses pip to install poetry, so we mount pip cache dir.
# The main installation script URL (install.python-poetry.org) is not available in Iran, so we use a mirror.
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    curl -sSL https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/main/install-poetry.py | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml ./

# Install main dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-root --only main

# Activate the virtualenv
ENV VIRTUAL_ENV="$PYSETUP_PATH/.venv" PATH="$PYSETUP_PATH/.venv/bin:$PATH"

##################################################### Development ######################################################
FROM builder-base AS development

RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

