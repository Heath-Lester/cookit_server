#!/bin/bash
rm -rf cookit_api/migrations
rm db.sqlite3
python3 manage.py migrate
python3 manage.py makemigrations cookit_api
python3 manage.py migrate cookit_api
python3 manage.py loaddata users
python3 manage.py loaddata tokens
