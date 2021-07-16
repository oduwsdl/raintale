#!/bin/bash

echo "starting GUI for Raintale"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DAEMONIZE_DJANGO=0
WOOEY_DIR=${SCRIPT_DIR}/../raintale_with_wooey
DJANGO_PORT=8000

while test $# -gt 0; do

    echo "looping..."

    case "$1" in
        --dont-daemize-django)
        DAEMONIZE_DJANGO=1
        ;;
        --wooey-dir)
        shift
        WOOEY_DIR=$1
        echo "setting WOOEY_DIR to ${WOOEY_DIR}"
        ;;
        --django-port)
        shift
        DJANGO_PORT=$1
        echo "setting DJANGO_PORT to ${DJANGO_PORT}"
        ;;
    esac

    shift

done

CELERY_PROJECT_NAME=`basename ${WOOEY_DIR}`

echo "changing directory to ${WOOEY_DIR}"
cd ${WOOEY_DIR}

echo "Starting celery"
# TODO: make this work, it is the preferred way of daemonizing celery
# celery multi start worker1 -A raintale_with_wooey -c 1 --beat -l info --logfile=celery-wooey.log --pidfile=celery-wooey.pid
celery -A ${CELERY_PROJECT_NAME} worker -c 1 --beat -l info > celery-output.log 2>&1 &
celery_pid=$!
echo "Celery PID is ${celery_pid}"
echo $celery_pid > celery-wooey.pid
echo "finished starting Celery"

if [ ${DAEMONIZE_DJANGO} -eq 0 ]; then
    python ./manage.py runserver 0.0.0.0:${DJANGO_PORT} > django-output.log 2>&1 &
    django_pid=$!
    echo "Django PID is ${django_pid}"
    echo $django_pid > django-wooey.pid
    echo "finished starting Django"
    echo "done starting GUI for Raintale"
else
    # so all future output comes from Django and goes to the screen
    python ./manage.py runserver 0:${DJANGO_PORT}
fi

