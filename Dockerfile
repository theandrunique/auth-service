FROM python:3.11-slim as builder

RUN python -m pip install poetry==1.8.2 

COPY pyproject.toml ./

RUN poetry export -o requirements.txt --without-hashes


FROM python:3.11-slim

WORKDIR /app

EXPOSE 8000

COPY --from=builder requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src src/

COPY logger_config.yml .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logger_config.yml"]