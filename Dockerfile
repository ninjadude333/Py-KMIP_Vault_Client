# Use an official Python image as a base
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Environment variable for config file path
ENV CONFIG_FILE_PATH="/app/config.ini"

# Define entrypoint to run the script with the configuration file
ENTRYPOINT ["python", "rotate_kmip_key.py"]
