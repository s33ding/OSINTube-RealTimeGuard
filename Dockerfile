# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

WORKDIR /app

COPY . .

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y vim git && \
    rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy just the requirements file
COPY requirements.txt .

# Install pip requirements
RUN python -m pip install -r requirements.txt

ENV USER="streamlit"


HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "home.py"]
