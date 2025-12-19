FROM python:3.11-slim

# Install git, curl, and docker CLI
RUN apt-get update && apt-get install -y \
    git \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install docker-compose standalone binary
RUN curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Fix "dubious ownership" error in git
RUN git config --global --add safe.directory /app

EXPOSE 9000

WORKDIR /app

# Copy the webhook script
COPY AUTOUPDATE_WEBHOOK_FROM_GITHUB.py .

# The CMD runs the script from the mounted volume location
CMD ["python", "core/TOOLS/AUTOUPDATE_WEBHOOK_FROM_GITHUB/AUTOUPDATE_WEBHOOK_FROM_GITHUB.py"]
