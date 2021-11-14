#!/bin/bash

set -e

echo "Configuring Raintale WUI for queueing service"
echo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../raintale_with_wooey"

POOL_LIMIT=1
CELERYD_CONCURRENCY=1

while test $# -gt 0; do

    case "$1" in
        --amqp-url)
        shift
        AMQP_URL=$1
        echo "setting AMQP URL to ${AMQP_URL} [ OK ]"
        ;;
        --pool-limit)
        shift
        POOL_LIMIT=$1
        echo "setting pool limit to ${POOL_LIMIT} [ OK ]"
        ;;
        --concurrency)
        shift
        CELERYD_CONCURRENCY=$1
        echo "setting concurrency to to ${CELERYD_CONCURRENCY} [ OK ]"
        ;;
    esac
    shift

done

if [ -z "${AMQP_URL}" ]; then
    echo "An AMQP URL is required."
    echo "You are missing one of the required arguments, please rerun with the missing value supplied. This is what I have:"
    echo "--amqp_url ${AMQP_URL}"
    echo "--pool_limit ${POOL_LIMIT}"
    echo "--concurrency ${CELERYD_CONCURRENCY}"
    echo
    exit 22 #EINVAL
fi

printf "Adding queuing service settings, like the AMQP URL of '${AMQP_URL}', to Django [    ]"

settings_file=${WOOEY_DIR}/raintale_with_wooey/settings/user_settings.py

cat >> ${settings_file} <<- EOF
CELERY_BROKER_URL = "${AMQP_URL}"
CELERY_BROKER_POOL_LIMIT = ${POOL_LIMIT}
CELERYD_CONCURRENCY = ${CELERYD_CONCURRENCY}
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ACKS_LATE = True
EOF
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
else
    printf "[ OK ]\n"
fi

echo
echo "You must restart the Raintale WUI service to start using the queueing service"
echo
echo "Done configuring Raintale WUI for queueing service"
