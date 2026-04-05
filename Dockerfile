FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by opencv-python
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy the rest of the project
COPY . .

# Install dependencies into system Python.
# This prevents conflicts if a local Windows .venv is mounted via docker volumes.
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Expose backend port
EXPOSE 8000

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
