# Use the official Python base image
FROM python:3.10-slim

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6

# Set the working directory in the container
WORKDIR /flask_lsc_inspector_app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn --no-cache-dir

# Copy the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set the CMD to start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "application:create_app()"]
