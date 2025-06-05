# Heimdallr Docker Container - Law Enforcement Use Only
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    wget \
    unzip \
    python3-dev \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && pip install --upgrade pip \
    && pip install dlib face_recognition

# Install Chrome for Selenium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN apt-get update && apt-get install -y curl wget unzip \
    && CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Heimdallr package
RUN pip install -e .

# Create non-root user for security
RUN useradd -m -u 1000 investigator && \
    chown -R investigator:investigator /app
USER investigator

# Create directories
RUN mkdir -p /app/results /app/cache /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV HEIMDALLR_DOCKER=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD heimdallr --help > /dev/null || exit 1

# Default command
CMD ["bash"]

# Usage instructions
LABEL org.opencontainers.image.title="Heimdallr"
LABEL org.opencontainers.image.description="Facial Recognition Search Tool - Law Enforcement Use Only"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Law Enforcement Technologies"
LABEL usage="docker run -it -v /host/cases:/app/results heimdallr:latest"
