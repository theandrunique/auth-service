FROM python:3.12.2-slim-bullseye as builder

COPY pyproject.toml poetry.lock ./

RUN python -m pip --no-cache-dir install poetry==1.8.2 && \
    apt update && \
    apt install -y --no-install-recommends gcc

RUN poetry export -o requirements.txt --without-hashes && \
    poetry export -o requirements.dev.txt --without-hashes --only dev

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels/dev -r requirements.dev.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels/prod -r requirements.txt

FROM python:3.12.2-slim-bullseye as build-base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000

FROM build-base as dev

COPY --from=builder /wheels/prod /wheels
COPY --from=builder /wheels/dev /wheels

RUN pip install --no-cache /wheels/* 

COPY . .

FROM build-base as prod

COPY --from=builder /wheels/prod /wheels

RUN pip install --no-cache /wheels/* 

COPY src src/
