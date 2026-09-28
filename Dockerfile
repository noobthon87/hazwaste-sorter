# HazWaste Sorter - Container Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and static assets
COPY . .

# Environment variables (Google Cloud Run default is 8080)
ENV PORT=8080
EXPOSE 8080

# Start server
CMD ["python", "server.py"]
