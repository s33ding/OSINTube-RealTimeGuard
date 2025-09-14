FROM python:3.9-slim

WORKDIR /app

# Install system packages
RUN apt-get update && \
    apt-get install -y vim git curl && \
    rm -rf /var/lib/apt/lists/*

# Python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements and install dependencies
COPY docker-image/requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy application code
COPY app ./app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Environment variables to override config
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_BASE_URL_PATH=${BASE_URL_PATH:-}
ENV STREAMLIT_BROWSER_SERVER_ADDRESS=${BROWSER_SERVER_ADDRESS:-localhost}

CMD ["streamlit", "run", "app/🏠_Home.py"]
