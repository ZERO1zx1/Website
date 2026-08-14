# Secure Code Execution Sandbox
# Minimal, isolated environment for running untrusted code

FROM python:3.11-slim

# Install only essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 runner

# Set working directory
WORKDIR /sandbox

# Copy runner and internal HTTP service
COPY runner.py /sandbox/runner.py
COPY service.py /sandbox/service.py

# Switch to non-root user
USER runner

# Set resource limits
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

# Default internal service entrypoint
CMD ["python", "/sandbox/service.py"]
