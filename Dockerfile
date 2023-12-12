# Use the official Python base image
FROM python:3.10-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn --no-cache-dir

# Copy the application code to the container
COPY . .

# Set the ENTRYPOINT to gunicorn
# and set the CMD to app:app to tell gunicorn what to run
ENTRYPOINT ["gunicorn", "application:create_app()"]
