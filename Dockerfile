# ================================
# Base Image
# ================================
FROM python:3.10-slim

# ================================
# Environment Settings
# ================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ================================
# System Dependencies
# ================================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ================================
# Working Directory
# ================================
WORKDIR /app

# ================================
# Install Python Dependencies
# ================================
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ================================
# Copy Application Code
# ================================
COPY backend ./backend

# ================================
# Expose Port
# ================================
EXPOSE 8000

# ================================
# Start FastAPI Server
# ================================
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
