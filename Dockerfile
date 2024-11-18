# Use a lightweight Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create directories for certificates, key output, logs, and config
RUN mkdir -p /app/certs /app/output /app/logs

# Set working directory
WORKDIR /app

# Copy the Python script, requirements file, and config file
COPY requirements.txt /app/
COPY ts-kmip-client.py /app/
COPY config.ini /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose directories as volumes
VOLUME ["/app/certs", "/app/output", "/app/logs", "/app/config"]

# Default command to run the Python script
CMD ["python", "ts-kmip-client.py"]
