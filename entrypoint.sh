#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python -c "
from urllib.parse import urlparse
import time
import psycopg2
from decouple import config

dsn = config('DATABASE_URL', default='')
if dsn:
    r = urlparse(dsn)
    dbname = r.path[1:]
    user = r.username
    password = r.password
    host = r.hostname
    port = r.port
else:
    dbname = config('DB_NAME', default='instagram_db')
    user = config('DB_USER', default='postgres')
    password = config('DB_PASSWORD', default='postgres')
    host = config('DB_HOST', default='db')
    port = config('DB_PORT', default='5432')

while True:
    try:
        psycopg2.connect(
            dbname=dbname, user=user, password=password,
            host=host, port=port,
        )
        break
    except psycopg2.OperationalError:
        time.sleep(1)
print('PostgreSQL is ready')
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -
