# Use Python as the base image
FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the container
COPY src/ ./src/
COPY config/ ./config/

# Expose the RabbitMQ default port (optional)
EXPOSE 5672

# Set the default command to run the pub-sub service
CMD ["python", "src/main.py"]