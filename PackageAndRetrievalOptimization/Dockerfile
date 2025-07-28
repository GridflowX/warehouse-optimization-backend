# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /PackageAndRetrievalOptimization

# Copy only requirements.txt first to cache dependencies layer
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your code
COPY . .

EXPOSE 8080
# Default command to run your script
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]