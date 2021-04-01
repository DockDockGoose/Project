#!/bin/sh

if [ "$DATABASE" = "mongodb" ]
then
    echo "Waiting for mongo..."

    while ! nc -z $MONGO_HOST $MONGO_PORT; do
      sleep 0.1
    done

    echo "mongoDB started"
fi

# This removes all data from db
# python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
exec "$@"