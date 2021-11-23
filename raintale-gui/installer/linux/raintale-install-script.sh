#!/bin/bash

set -e

function test_command(){
    command=$1

    printf "checking for command: $command [    ]"

    set +e
    which $command > /dev/null
    status=$?

    if [ $status -ne 0 ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "the command '$command' is required to install Raintale; it was not detected in your PATH"
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

    set -e
}

function test_access() {
    directory=$1
    printf "verifying that user `whoami` has write access to $directory [    ]"

    set +e
    touch ${directory}/raintale-install-testfile.deleteme > /dev/null 2>&1
    status=$?

    printf "\b\b\b\b\b"

    if [ $status -ne 0 ]; then
        
        printf "FAIL]\n"
        echo "this installer needs to be able to write to '${directory}', which `whoami` cannot write to, please run it as a user with these permissions"
        exit 22
    fi

    rm ${directory}/raintale-install-testfile.deleteme
    printf " OK ]\n"

    set -e
}

function run_command() {
    text_to_print=$1
    command_to_run=$2
    newline=$3

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
        exit 2
    fi

    if [ $newline == "nonewline" ]; then
        printf "[ OK ]"
    else
        printf "[ OK ]\n"
    fi

    set -e
}

function verify_absolute_path() {
    directory_to_check=$1

    printf "checking if $directory_to_check is an absolute path [    ]"
    printf "\b\b\b\b\b\b"

    if [ "${directory_to_check:0:1}" = "/" ]; then
        printf "[ OK ]\n"
        absolute_path_check=0
    else
        printf "[FAIL]\n"
        absolute_path_check=1
    fi
}

function create_tellstory_wrapper_script() {

    wrapper_script_path=$1

    printf "establishing wrapper script in ${wrapper_script_path}/tellstory for Raintale CLI [    ]"

    set +e
    cat <<EOF > ${wrapper_script_path}/tellstory
#!/bin/bash
source ${INSTALL_DIRECTORY}/raintale-virtualenv/bin/activate
${INSTALL_DIRECTORY}/raintale-virtualenv/bin/tellstory \$@
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Raintale CLI wrapper script at ${wrapper_script_path}/tellstory"
        exit 2
    fi
    set -e
}

function check_for_systemctl() {
    printf "checking for systemctl -- does this server run systemd? [    ]"

    set +e
    which systemctl
    status=$?
    SYSTEMD_SERVER=$status

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
        systemctl_check=0
    else
        printf "[ NO ]\n"
        systemctl_check=1
    fi
    set -e
}

function check_for_systemd() {
    printf "checking for systemd [    ]"

    printf "\b\b\b\b\b\b"

    # not all systemd servers have this directory
    # checkdir="/run/systemd/system"

    # Ubuntu 21.04 and Centos 8 have this directory
    checkdir="/etc/systemd/system"

    if [[ -e ${checkdir} ]]; then
        printf "[ OK ]\n"
        systemd_check=0
    else
        printf "[ NO ]\n"
        systemd_check=1
    fi

}

function check_for_checkconfig() {
    printf "checking for checkconfig -- does this server use initd runlevels instead of systemd? [    ]"

    set +e
    which systemctl > /dev/null
    status=$?
    SYSTEMD_SERVER=$status

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
        checkconfig_check=0
    else
        printf "[ NO ]\n"
        checkconfig_check=1
    fi
    set -e
}

function create_generic_startup_scripts() {

    printf "creating startup wrapper [    ]"

    set +e
    cat <<EOF > ${INSTALL_DIRECTORY}/start-raintale-wui.sh
#!/bin/bash
source ${INSTALL_DIRECTORY}/raintale-virtualenv/bin/activate
${INSTALL_DIRECTORY}/raintale-gui/start-raintale-wui.sh --django-port ${DJANGO_PORT}
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Raintale startup wrapper"
        exit 2
    fi
    set -e

    printf "creating shutdown wrapper [    ]"

    set +e
    cat <<EOF > ${INSTALL_DIRECTORY}/stop-raintale-wui.sh
#!/bin/bash
source ${INSTALL_DIRECTORY}/raintale-virtualenv/bin/activate
${INSTALL_DIRECTORY}/raintale-gui/stop-raintale-wui.sh
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Raintale startup wrapper"
        exit 2
    fi
    set -e

    run_command "setting permissions on startup wrapper" "chmod 0755 ${INSTALL_DIRECTORY}/start-raintale-wui.sh"
    run_command "setting permissions on shutdown wrapper" "chmod 0755 ${INSTALL_DIRECTORY}/stop-raintale-wui.sh"
}

function create_systemd_startup() {
    printf "creating systemd Raintale Celery service file [    ]"

    set +e
    cat <<EOF > /etc/systemd/system/raintale-celery.service
[Unit]
Description=The Raintale WUI Celery service
After=syslog.target network.target remote-fs.target nss-lookup.target

[Service]
ExecStart=${INSTALL_DIRECTORY}/raintale-virtualenv/bin/celery -A raintale_with_wooey worker --beat -l info
User=${RAINTALE_USER}
WorkingDirectory=${INSTALL_DIRECTORY}/raintale_with_wooey
EnvironmentFile=/etc/raintale.conf

[Install]
WantedBy=multi-user.target
EOF

    status=$?
    set -e

    printf "\b\b\b\b\b\b"
    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        exit 2
    fi

    printf "creating systemd Raintale Django service file [    ]"

    set +e
    cat <<EOF > /etc/systemd/system/raintale-django.service
[Unit]
Description=The Raintale WUI Django service
After=raintale-celery.service
Requires=raintale-celery.service

[Service]
ExecStart=${INSTALL_DIRECTORY}/raintale-virtualenv/bin/python manage.py runserver ${DJANGO_IP}:${DJANGO_PORT}
User=${RAINTALE_USER}
WorkingDirectory=${INSTALL_DIRECTORY}/raintale_with_wooey
EnvironmentFile=/etc/raintale.conf

[Install]
WantedBy=multi-user.target
EOF
    status=$?
    set -e

    printf "\b\b\b\b\b\b"
    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        exit 2
    fi
}

function perform_install() {

    test_command "ls"
    test_command "mkdir"
    test_command "touch"
    test_command "whoami"
    test_command "tar"
    test_command "dirname"
    test_command "python"
    test_command "grep"
    test_command "virtualenv"

    test_access `dirname ${INSTALL_DIRECTORY}`
    test_access "/etc"

    run_command "setting install directory to $INSTALL_DIRECTORY" ""

    verify_absolute_path "$INSTALL_DIRECTORY"
    if [ $absolute_path_check -ne 0 ]; then
        echo "please specify an absolute path for the installation directory"    
        exit 22
    fi

    run_command "creating $INSTALL_DIRECTORY" "mkdir -p $INSTALL_DIRECTORY"
    run_command "creating ${INSTALL_DIRECTORY}/var/run" "mkdir -p $INSTALL_DIRECTORY/var/run"
    run_command "creating ${INSTALL_DIRECTORY}/var/log" "mkdir -p $INSTALL_DIRECTORY/var/log"
    run_command "removing existing virtualenv, if present" "rm -rf $INSTALL_DIRECTORY/raintale-virtualenv"
    run_command "creating virtualenv for Raintale" "virtualenv -p $PYTHON_EXE $INSTALL_DIRECTORY/raintale-virtualenv"

    run_command "discovering Raintale CLI and libraries archive" "ls raintale*.tar.gz | grep -v 'gui'"
    CLI_TARBALL=`cat ${command_output_file}`
    run_command "discovering Raintale GUI archive" "ls raintale-gui-*.tar.gz"
    GUI_TARBALL=`cat ${command_output_file}`

    # in some environments --no-cache-dir avoids the enormous memory consumption of pytorch installation
    # see: https://github.com/pytorch/pytorch/issues/1022
    run_command "installing Raintale CLI and libraries in virtualenv" "(${INSTALL_DIRECTORY}/raintale-virtualenv/bin/pip install --no-cache-dir ${CLI_TARBALL})"
    run_command "extracting Raintale WUI" "tar -C ${INSTALL_DIRECTORY} -x -v -z -f ${GUI_TARBALL}"

    create_tellstory_wrapper_script "${WRAPPER_SCRIPT_PATH}"

    run_command "setting permissions on Raintale CLI wrapper script" "chmod 0755 ${WRAPPER_SCRIPT_PATH}/tellstory"
    run_command "setting permissions on Raintale database configuration script" "chmod 0755 ${INSTALL_DIRECTORY}/raintale-gui/set-raintale-database.sh"
    run_command "setting permissions on Raintale queueing service configuration script" "chmod 0755 ${INSTALL_DIRECTORY}/raintale-gui/set-raintale-queueing-service.sh"

    if [ ${SKIP_SCRIPT_INSTALL} -eq 0 ]; then
        run_command "creating Raintale WUI" "(source ${INSTALL_DIRECTORY}/raintale-virtualenv/bin/activate && ${INSTALL_DIRECTORY}/raintale-gui/install-raintale-wui.sh --skip-script-install)"
    else
        run_command "creating Raintale WUI" "(source ${INSTALL_DIRECTORY}/raintale-virtualenv/bin/activate && ${INSTALL_DIRECTORY}/raintale-gui/install-raintale-wui.sh)"
    fi
    # TODO: set Debug=False in django_settings.py

    if [ $FORCE_SYSTEMD -eq 0 ]; then
        create_systemd_startup
    fi

    run_command "setting permissions on Raintale directories" "find ${INSTALL_DIRECTORY} -type d -exec chmod 0755 {} \;"

    # check_for_systemctl
    # if [ $systemctl_check -ne 0 ]; then
    check_for_systemd
    if [ $systemd_check -ne 0 ]; then
        check_for_checkconfig
        if [ $checkconfig_check -ne 0 ]; then
            create_generic_startup_scripts
            echo
            echo "Notes:"
            echo "* to start the Raintale WUI, run ${INSTALL_DIRECTORY}/start-raintale-wui.sh"
            echo "* to stop the Raintale WUI, run ${INSTALL_DIRECTORY}/stop-raintale-wui.sh"

            # TODO: check for macOS and create an icon or something in /Applications for the user to start it there
        else
            create_initd_startup
        fi
    else
        create_systemd_startup
    fi
}

# install starts here

echo
echo "Welcome to Raintale - beginning Unix/Linux install"
echo

INSTALL_DIRECTORY="/opt/raintale"
DJANGO_PORT=8100
DJANGO_IP="0.0.0.0"
RAINTALE_USER="root"
WRAPPER_SCRIPT_PATH="/usr/local/bin"
FORCE_SYSTEMD=1
FORCE_INITD=1
PYTHON_EXE="/usr/bin/python"
SKIP_SCRIPT_INSTALL=1

while test $# -gt 0; do

    case "$1" in
        --install-directory) 
        shift
        INSTALL_DIRECTORY=$1
        ;;
        --service-port)
        shift
        DJANGO_PORT=$1
        ;;
        --cli-wrapper-path)
        shift
        WRAPPER_SCRIPT_PATH=$1
        ;;
        --raintale-user)
        shift
        RAINTALE_USER=$1
        ;;
        --force-systemd)
        FORCE_SYSTEMD=0
        ;;
        --python-exe)
        shift
        PYTHON_EXE=$1
        ;;
        --force-initd)
        shift
        FORCE_INITD=0
        ;;
        --django_IP)
        shift
        DJANGO_IP=$1
        ;;
        --skip-script-install)
        SKIP_SCRIPT_INSTALL=0
        ;;
    esac
    shift

done

perform_install $@

echo
echo "Done with Unix/Linux install. Please read the documentation for details on more setup options and how to use Raintale."
