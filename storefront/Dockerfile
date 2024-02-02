# Use the official Python image as the base image
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install --upgrade pip \
    && pip install gunicorn \
    && pip install -r requirements.txt \
    && apk del build-deps

# Copy the Django project files to the working directory
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the Python script to fetch IP and start Gunicorn
CMD ["gunicorn", "storefront.wsgi:application"]
