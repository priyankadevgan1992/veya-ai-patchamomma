FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/veya_data

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Command to run the backend server
CMD ["python", "-m", "uvicorn", "veya_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
