#!/bin/bash
python manage.py showmigrations
python manage.py makemigrations products
python manage.py migrate
python manage.py shell < create_superuser.py
gunicorn flicks.wsgi:application

