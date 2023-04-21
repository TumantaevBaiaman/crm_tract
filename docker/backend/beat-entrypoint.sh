#!/bin/sh

until cd /app/backend
do
    echo "Waiting for server volume..."
done

celery -A crm_tract beat -l info

