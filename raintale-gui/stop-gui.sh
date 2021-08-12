#!/bin/bash

echo "beginning the steps to shut down Raintale GUI"

WOOEY_DIR="../raintale_with_wooey"

cd ${WOOEY_DIR}

django_pid=`cat django-wooey.pid`
echo "stopping Django at PID ${django_pid}"
kill ${django_pid}
echo "Django should be stopped"
rm django-wooey.pid

celery_pid=`cat celery-wooey.pid`
echo "stopping Celery at PID ${celery_pid}"
kill ${celery_pid}
# ps -ef | grep celery | grep -v grep | awk '{ print $2 }' | tr '\n' ' ' | xargs kill
echo "Celery should be stopped"
rm celery-wooey.pid

echo "Raintale GUI processes should be shut down"
