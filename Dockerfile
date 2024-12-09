# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu

# Copy the project files
COPY pipeline.py .
COPY startup.py .
COPY api.py .
COPY search.py . 

# Create directories for data and vectordb
RUN mkdir -p /app/data/2021
RUN mkdir -p /app/vectordb_workspace

# Expose the API port
EXPOSE 8000

# Set environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

# Install Spark
RUN wget https://downloads.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz \
    && tar -xzf spark-3.2.1-bin-hadoop3.2.tgz \
    && mv spark-3.2.1-bin-hadoop3.2 /opt/spark \
    && rm spark-3.2.1-bin-hadoop3.2.tgz