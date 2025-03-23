FROM python:3.13-slim-bookworm

# Set working directory inside container
WORKDIR /app/backend

# Copy only files needed for installing dependencies
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv
RUN pip install --upgrade pip && \
    pip install uv uvicorn fastapi && \
    uv sync --project .

# Copy the rest of the backend code
COPY . .

# Expose backend port
EXPOSE 8000

# Run backend with autoreload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
