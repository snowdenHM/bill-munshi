# Use the python:3.9-buster image as a parent image
FROM python:3.9-buster

# Set environment variables for Python buffering and Django settings
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE v1_bill.settings

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose port 8000 for the Gunicorn server
EXPOSE 8000

# Apply migrations and create a superuser
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'billmunshi')" | python manage.py shell

# Run Gunicorn to serve the Django application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "v1_bill.wsgi:application"]
