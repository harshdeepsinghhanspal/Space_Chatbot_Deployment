# Use a lightweight Python 3.10 base image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for Rust-based builds
RUN apt-get update && apt-get install -y cargo build-essential

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for FastAPI
EXPOSE 10000

# Command to run your FastAPI app
CMD ["uvicorn", "Gradio_Proj:app", "--host", "0.0.0.0", "--port", "10000"]
