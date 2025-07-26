FROM python:3.13-slim-bookworm

# Set working directory inside container
WORKDIR /app/backend

# Copy only files needed for installing dependencies
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv into .venv
RUN pip install --upgrade pip uv \
    && uv sync --project .

# Add the venv's bin directory to PATH so that `python` and `uvicorn` from .venv are used
ENV VENV_PATH=/app/backend/.venv
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy the rest of the backend code
COPY . .

# Expose backend port
EXPOSE 8000

# Run backend with autoreload (now using uvicorn from .venv)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
