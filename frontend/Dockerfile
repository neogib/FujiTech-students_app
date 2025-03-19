FROM node:16

# Set the working directory for the frontend
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy dependency files (package.json and optionally pnpm-lock.yaml)
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Install dependencies using pnpm
RUN pnpm install

# Copy all frontend code into the working directory
COPY frontend/ .

# Inform Docker that the application will run on port 3000
EXPOSE 3000

# Run the frontend application
CMD ["pnpm", "dev"]

