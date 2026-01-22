FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy xml parser code only
COPY xmlparser/ ./xmlparser/

# Ensure logs flush immediately
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "xmlparser.main"]