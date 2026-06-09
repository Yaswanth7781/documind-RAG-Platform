FROM python:3.11-slim
WORKDIR /app
COPY audit-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY audit-service/ ./audit-service/
# Shared module will be mapped or copied here
ENV PYTHONPATH=/app
WORKDIR /app/audit-service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
