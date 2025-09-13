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
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy application code
COPY app ./app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app/home.py", "--server.address", "0.0.0.0"]
