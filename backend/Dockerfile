FROM python:3.9-slim

# Set the working directory inside the container for the backend
WORKDIR /app/backend

# Copy all backend code into the working directory
COPY backend/ .

# Upgrade pip, install the 'uv' tool, and synchronize project dependencies using uv
RUN pip install --upgrade pip && pip install uv && uv sync --project .

# Inform Docker that the application will use port 8000
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
