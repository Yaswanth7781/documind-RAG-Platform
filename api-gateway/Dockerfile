FROM python:3.11-slim
WORKDIR /app
COPY api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api-gateway/ ./api-gateway/
# Also need shared folder if we depend on it, but api gateway doesn't strictly need it unless we validate JWT here.
# Let's mount or copy it. Assuming docker-compose maps it.
WORKDIR /app/api-gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
