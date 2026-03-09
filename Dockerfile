# Use the official Python Alpine or Slim image. 
# Slim is often better for ML libraries to avoid missing C-extensions.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for OCR
# tesseract-ocr is the core engine
# libgl1-mesa-glx may be needed by opencv if python-opencv is added later
# poppler-utils provides pdftoppm which pdf2image uses to parse PDFs
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy En-Core model if required as base by other scripts
RUN python -m spacy download en_core_web_sm

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Set environment variables for Poppler and Tesseract if needed
ENV POPPLER_PATH=/usr/bin
ENV TESSERACT_CMD_PATH=/usr/bin/tesseract

# Expose port 5000 for FastAPI
EXPOSE 5000

# Command to run the application using uvicorn
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "5000"]
