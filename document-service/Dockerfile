FROM python:3.11-slim
WORKDIR /app
COPY document-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY document-service/ ./document-service/
# Shared module will be mapped or copied here
ENV PYTHONPATH=/app
WORKDIR /app/document-service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
