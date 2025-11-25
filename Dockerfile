# =============================================================================
# JPAPI Docker Image
# =============================================================================
# Usage: docker run -it --rm jpapi/jpapi:latest
# =============================================================================

FROM python:3.11-slim

# Set metadata
LABEL maintainer="JPAPI Team"
LABEL description="JAMF Pro API Toolkit"
LABEL version="2.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install JPAPI in editable mode
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 jpapi
USER jpapi

# Set entrypoint
ENTRYPOINT ["jpapi"]
CMD ["--help"]
