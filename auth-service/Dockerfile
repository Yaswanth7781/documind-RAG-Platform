FROM python:3.11-slim
WORKDIR /app
COPY auth-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY auth-service/ ./auth-service/
# Shared module will be mapped or copied here
ENV PYTHONPATH=/app
WORKDIR /app/auth-service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
