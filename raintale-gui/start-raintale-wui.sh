#!/bin/bash

echo "Starting Raintale WUI"
echo

function run_command() {
    text_to_print=$1
    command_to_run=$2
    error_text=$3
    newline=$4

    if [ -z $newline ]; then
        newline="yes"
    fi

    printf "${text_to_print} [    ]"

    command_output_file=`mktemp`

    set +e

    eval "$command_to_run" > $command_output_file 2>&1
    status=$?

    printf "\b\b\b\b\b\b"
    if [ $status -ne 0 ]; then
        
        printf "[FAIL]\n"
        echo
        cat "$command_output_file"
        echo
        echo "${text_to_print} FAILED"
        echo
        echo "${error_text}"
        exit 2
    fi

    if [ $newline == "nonewline" ]; then
        printf "[ OK ]"
    else
        printf "[ OK ]\n"
    fi

    set -e
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DAEMONIZE_DJANGO=0
WOOEY_DIR=${SCRIPT_DIR}/../raintale_with_wooey
DJANGO_PORT=8000
DJANGO_IP=0.0.0.0

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
        --django-ip)
        DJANGO_IP=$1
        run_command "setting DJANGO_IP to ${DJANGO_IP}" ""
        ;;
    esac

    shift

done

printf "starting Raintale Celery Service [    ]"

CELERY_PROJECT_NAME=`basename ${WOOEY_DIR}`

#echo "changing directory to ${WOOEY_DIR}"
cd ${WOOEY_DIR}

# TODO: make this work, it is the preferred way of daemonizing celery
# celery multi start worker1 -A hypercane_with_wooey -c 1 --beat -l info --logfile=celery-wooey.log --pidfile=celery-wooey.pid
set +e
celery -A ${CELERY_PROJECT_NAME} worker --beat -l info > celery-output.log 2>&1 &
status=$?
celery_pid=$!

printf "\b\b\b\b\b\b"

if [ $status -ne 0 ]; then
    printf "[FAIL]\n"

    echo
    echo "FAIL: Raintale Celery could not be started"
    echo 
    exit $status
else
    printf "[ OK ]\n"
fi

set -e
echo $celery_pid > celery-wooey.pid

if [ ${DAEMONIZE_DJANGO} -eq 0 ]; then

    printf "starting Raintale Django Service on ${DJANGO_IP}:${DJANGO_PORT} [    ]"
    python ./manage.py runserver ${DJANGO_IP}:${DJANGO_PORT} > django-output.log 2>&1 &
    django_pid=$!
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -ne 0 ]; then

        printf "[FAIL]\n"

        echo
        echo "FAIL: Raintale Django could not be started on ${DJANGO_IP}:${DJANGO_PORT}"
        echo
        cat django-output.log
        echo
        exit $status
    else
        printf "[ OK ]\n"
    fi

    echo $django_pid > django-wooey.pid
else
    # for development, so all future output comes from Django and goes to the screen
    printf "starting Raintale Django Service with output to screen \n"
    python ./manage.py runserver ${DJANGO_IP}:${DJANGO_PORT}
fi

echo
echo "Done starting Raintale WUI"