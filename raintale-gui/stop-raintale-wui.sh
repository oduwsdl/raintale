#!/bin/bash

echo "Stopping Raintale WUI"
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
    else
        if [ $newline == "nonewline" ]; then
            printf "[ OK ]"
        else
            printf "[ OK ]\n"
        fi
    fi

    set -e
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../raintale_with_wooey"

django_pid=`cat "${WOOEY_DIR}/django-wooey.pid"`
run_command "stopping Django at process ID ${django_pid}" "kill ${django_pid}"
run_command "removing PID file at ${WOOEY_DIR}/django-wooey.pid" "rm \"${WOOEY_DIR}/django-wooey.pid\""

celery_pid=`cat "${WOOEY_DIR}/celery-wooey.pid"`
# run_command "stopping Celery at PID ${celery_pid}" "kill ${celery_pid}"

printf "stopping Celery at process ID $PID ${celery_pid} "

celery_proc_count=`ps -ef | grep ${celery_pid} | grep "raintale_with_wooey" | grep -v grep | awk '{ print $2 }' | wc -l`

attempt_count=0
attempts_left=5

while [ $celery_proc_count -ne 0 ]; do

    celery_procs=`ps -ef | grep ${celery_pid} | grep "raintale_with_wooey" | grep -v grep | awk '{ print $2 }'`

    for pid in `echo ${celery_procs}`; do
        printf "sending TERM signal to pid ${pid}\n"
        kill $pid
    done

    printf "sleeping for 5 seconds before checking again "

    for i in `seq 1 5`; do
        
        sleep 1
        printf ". "
    done

    printf "\n"

    if [ $attempts_left -le 0 ]; then
        printf "no longer attempting graceful Celery shutdown with TERM signal, resorting to KILL signal"

        for pid in `echo ${celery_procs}`; do
            printf "sending KILL signal to pid ${pid}\n"
            kill -9 $pid
        done
    fi

    celery_proc_count=`ps -ef | grep ${celery_pid} | grep "raintale_with_wooey" | grep -v grep | awk '{ print $2 }' | wc -l`

    # when expr evaluates to 0, it returns a nonzero status
    set +e
    attempt_count=`expr $attempt_count + 1`
    attempts_left=`expr 5 - $attempt_count`
    set -e
    echo "${attempts_left} attempts to stop Celery left"

done

celery_proc_count=`ps -ef | grep ${celery_pid} | grep "raintale_with_wooey" | grep -v grep | awk '{ print $2 }' | wc -l`

if [ $celery_proc_count -gt 0 ]; then
    printf "attempt to kill Celery failed, you will need to manually kill the processes\n"
    exit 2
else
    printf "successfully stopped Celery\n"
fi

run_command "removing PID file at ${WOOEY_DIR}/celery-wooey.pid" "rm \"${WOOEY_DIR}/celery-wooey.pid\""

echo
echo "Done stopping Raintale WUI"