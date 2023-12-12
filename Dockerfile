# Use the official Python base image
FROM python:3.10-slim

ARG FLASK_ENV
ARG FLASK_APP
ARG SQLALCHEMY_DB_URI
ARG JWT_SECRET_KEY
ARG FLASK_DEBUG
ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG SUPABASE_BUCKET_FILES
ARG SUPABASE_BUCKET_WEIGHTS
ARG SUPABASE_BUCKET_PROFILE_IMAGES
ARG ROBOFLOW_API_KEY
ARG ROBOFLOW_PROJECT

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

# Set environment variables
ENV FLASK_ENV=${FLASK_ENV}
ENV FLASK_APP=${FLASK_APP}
ENV SQLALCHEMY_DB_URI=${SQLALCHEMY_DB_URI}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENV FLASK_DEBUG=${FLASK_DEBUG}
ENV SUPABASE_URL=${SUPABASE_URL}
ENV SUPABASE_KEY=${SUPABASE_KEY}
ENV SUPABASE_BUCKET_FILES=${SUPABASE_BUCKET_FILES}
ENV SUPABASE_BUCKET_WEIGHTS=${SUPABASE_BUCKET_WEIGHTS}
ENV SUPABASE_BUCKET_PROFILE_IMAGES=${SUPABASE_BUCKET_PROFILE_IMAGES}
ENV ROBOFLOW_API_KEY=${ROBOFLOW_API_KEY}
ENV ROBOFLOW_PROJECT=${ROBOFLOW_PROJECT}

# Set the ENTRYPOINT to gunicorn
# and set the CMD to app:app to tell gunicorn what to run
ENTRYPOINT ["gunicorn", "application:create_app"]
