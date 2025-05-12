# Use official Python slim image without high vulnerabilities
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose application port
EXPOSE 5001

# Default command to run the app
CMD ["python", "run.py"]
