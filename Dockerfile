# Stage 1: Builder
FROM python:3.13 AS builder

# Set the working directory in the container
WORKDIR /app

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.13

# Set the working directory in the container
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /venv /venv

# Copy the application files
COPY . .

# Set the PATH to include the virtual environment
ENV PATH="/venv/bin:$PATH"

# Expose the port FastAPI runs on
EXPOSE 8000
