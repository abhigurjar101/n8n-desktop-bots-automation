FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/
COPY cli.py .

EXPOSE 8000

ENV N8N_BASE_URL=http://localhost:5678
ENV QDRANT_URL=http://localhost:6333
ENV WEB_PORT=8000
ENV WEB_HOST=0.0.0.0

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
