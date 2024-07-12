FROM python:3.12.2-slim-bullseye as builder

COPY pyproject.toml poetry.lock ./

RUN python -m pip --no-cache-dir install poetry==1.8.2 && \
    apt update && \
    apt install -y --no-install-recommends gcc && \
    poetry export -o requirements.txt --without-hashes && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.12.2-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000

COPY --from=builder /wheels /wheels

RUN pip install --no-cache /wheels/* 

COPY src src/

COPY logger_config.yml .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logger_config.yml"]
