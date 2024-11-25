# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV MONGODB_URL="mongodb://mongo:lIQkYOSUxBAyovSBVtDIfjdGnSgaBfDU@mongodb-4gp4.railway.internal:27017"
ENV OTEL_SDK_DISABLED=true

# Expose the port the app runs on
EXPOSE 8000

# Add a health check for port 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl --fail http://localhost:8000/ || exit 1

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
