FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install packages in groups to handle dependencies better
RUN pip install --no-cache-dir \
    Flask==2.3.3 \
    Flask-Cors==4.0.0 \
    Flask-SocketIO==5.5.1 \
    requests==2.31.0 \
    python-dotenv==1.1.1 \
    fastapi==0.116.1 \
    uvicorn==0.35.0 \
    conductor-python==1.0.54 \
    elasticsearch==9.1.0 \
    pymongo==4.13.2 \
    groq==0.30.0 \
    PyGithub==2.6.1 \
    reportlab==4.4.3 \
    pillow==11.3.0 \
    cryptography==45.0.5 \
    aiohttp==3.8.1 \
    pydantic==2.11.7 \
    httpx==0.28.1

# Copy everything
COPY . .

# Expose port 7000
EXPOSE 7000

# Start the Flask app
CMD ["python", "app.py"]