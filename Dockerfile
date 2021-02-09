FROM python:slim

RUN apt-get update \
    && apt-get -y install unzip \
    && apt-get -y install libaio-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN groupadd -g 1501 appuser
RUN useradd -r -g 1501 -u 1501 appuser
COPY app app
RUN chown -R appuser:appuser /app
COPY $AUTH_PRIVATE_KEY_FILE .
RUN chown -R appuser:appuser $AUTH_PRIVATE_KEY_FILE
USER appuser

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "$WORKERS_COUNT", "--log-level", "$LOGGING_LEVEL"]
