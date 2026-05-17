# Base image — Python 3.11 minimal installation
FROM python:3.11-slim

# Set working directory for all subsequent instructions
WORKDIR /app

# Copy dependency list first for layer caching optimisation
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Document that this container listens on port 8000
EXPOSE 8000

# Start the FastAPI application using uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]