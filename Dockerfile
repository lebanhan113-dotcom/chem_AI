FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EDUPLAN_DATA_DIR=/data EDUPLAN_ENV=production
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libreoffice-writer fonts-dejavu-core fonts-liberation gosu ca-certificates && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 edupuser
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
RUN chmod +x /app/start-online.sh && mkdir -p /data && chown -R edupuser:edupuser /app /data
EXPOSE 10000
CMD ["/app/start-online.sh"]
