FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/runtime
ENV ENVIRONMENT=production
EXPOSE 8000
CMD ["sh","-c","uvicorn server:APP --host 0.0.0.0 --port ${PORT:-8000}"]
