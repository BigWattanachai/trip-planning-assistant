# Use official Python image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the backend port (update if main.py uses a different port)
EXPOSE 8000

# Set environment variables (optional, for unbuffered output)
ENV PYTHONUNBUFFERED=1

# Command to run the backend (update if main.py needs arguments)
CMD ["python", "main.py"]
