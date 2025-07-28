FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application
COPY pdf_extractor.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set executable permissions
RUN chmod +x pdf_extractor.py

# Run the application
CMD ["python", "pdf_extractor.py"]