# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system packages for PyMuPDF and other libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to cache the pip install step
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir keeps the container size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose port 7860 for the web server (Required by Hugging Face Spaces)
EXPOSE 7860

# Start the application using Gunicorn (production web server for Flask)
# We use 1 worker and a high timeout (120s) because AI models take time to run and use lots of memory
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "run:app"]
