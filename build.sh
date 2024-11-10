#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# https://docs.djangoproject.com/en/3.0/ref/django-admin/#django-admin-createsuperuser
python manage.py createsuperuser --email "" --username "admin" --no-input