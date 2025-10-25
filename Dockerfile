# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first to cache installs
COPY requirements.txt .

# Install system deps (optional) + Python deps
RUN apt-get update && apt-get install -y build-essential
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Run your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
