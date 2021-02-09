FROM python:slim

RUN apt-get update \
    && apt-get -y install unzip \
    && apt-get -y install libaio-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN groupadd -g 1501 appuser
RUN useradd -r -g 1501 -u 1501 appuser
USER appuser
COPY app app
COPY $AUTH_PRIVATE_KEY_FILE .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "$WORKERS_COUNT", "--log-level", "$LOGGING_LEVEL"]
