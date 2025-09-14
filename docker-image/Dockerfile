FROM python:3.9-slim

WORKDIR /app

# Python environment (set early)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system packages
RUN apt-get update && \
    apt-get install -y vim git curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies (before app code for better caching)
COPY docker-image/requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application code (last to maximize cache hits)
COPY app/* ./

# Environment variables
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_BASE_URL_PATH=${BASE_URL_PATH:-}
ENV STREAMLIT_BROWSER_SERVER_ADDRESS=${BROWSER_SERVER_ADDRESS:-localhost}

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "🏠_Home.py"]
