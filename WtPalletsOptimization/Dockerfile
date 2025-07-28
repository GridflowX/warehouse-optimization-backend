# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /WtPalletsOptimization

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the container
COPY . .

# Set default command (optional)
# You can run a specific experiment script by overriding this at runtime
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
