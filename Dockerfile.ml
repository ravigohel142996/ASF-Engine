# ML Service Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Create models directory
RUN mkdir -p /app/models

# Expose port (if needed for future API)
EXPOSE 8002

# Run ML service (background training/prediction service)
CMD ["python", "-m", "src.models.hybrid_model"]
