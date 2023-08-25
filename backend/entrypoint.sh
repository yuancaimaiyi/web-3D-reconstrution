#!/bin/sh

# Example of Meshroom launching
# python3 launch.py /app/Meshroom /app/pipeline_graph_template.mg /app/media/datasets/<unique_dataset_name>
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python3 manage.py flush --no-input
python3 manage.py migrate --noinput

# "Do everything in this .sh script, then in the same shell run the command the user passes in on the command line"
exec "$@"