# Pull base image
FROM python:3.10.12-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    file \
    && rm -rf /var/lib/apt/lists/*
    
# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

# Backend Entrypoint
COPY .entrypoint.sh /entrypoint.sh
RUN chmod o+x /entrypoint.sh

# Copy project
COPY . .

EXPOSE 8000
ENV PORT 8000
ENV HOSTNAME "localhost"


ENTRYPOINT ["sh", "-c", " /entrypoint.sh"]