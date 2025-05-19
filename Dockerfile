FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

WORKDIR /app

# Copy requirements and install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir waitress

# Copy application code
COPY . .

# Install wget for health checks
RUN apt-get update && apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD [ "waitress-serve", "--port=8080", "wsgi:application"]
