#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CLI_SRC_DIR="${SCRIPT_DIR}/../../.."

function test_command(){
    command=$1

    printf "checking for $command [    ]"

    set +e
    which $command > /dev/null
    status=$?

    if [ $status -ne 0 ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "$command is required to create an installer"
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

    set -e
}

function test_python_version(){
    desired_version=$1
    PYTHON_VERSION=`python --version | sed 's/Python //g' | awk -F. '{ print $1 }'`

    printf "checking for Python version ${desired_version} [    ]"

    if [ $PYTHON_VERSION -ne ${desired_version} ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "Python version $PYTHON_VERSION is not supported, 3 is required."
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

}

function run_command() {
    text_to_print=$1
    command_to_run=$2
    newline=$3

    # echo "executing: ${command_to_run}"

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

echo "STARTING: Raintale installer build"

test_command "rm"
test_command "tar"
test_command "sed"
test_command "grep"
test_command "mktemp"
test_command "makeself"
test_command "python"
test_python_version "3"

run_command "acquiring Raintale version" "(grep '__appversion__ = ' ${CLI_SRC_DIR}/raintale/version.py) | sed 's/.*__appversion__ = //g'" "nonewline"
raintale_version=`cat ${command_output_file} | sed "s/'//g"`
echo " --- Raintale version is ${raintale_version}"

run_command "cleaning Raintale CLI and library build environment" "(cd ${CLI_SRC_DIR} && python ./setup.py clean 2>&1)"
run_command "cleaning Raintale CLI and library build environment" "(cd ${CLI_SRC_DIR} && rm -rf build dist 2>&1)"
run_command "cleaning installer directory" "rm -rf ${CLI_SRC_DIR}/installer/generic-unix"
run_command "building Raintale CLI and library install" "(cd ${CLI_SRC_DIR} && python ./setup.py sdist 2>&1)"

normalized_raintale_version=${raintale_version}

run_command "verifying Raintale CLI and library tarball" "ls ${CLI_SRC_DIR}/dist/raintale-${normalized_raintale_version}.tar.gz" "nonewline"
echo " --- ${CLI_SRC_DIR}/dist/raintale-${normalized_raintale_version}.tar.gz exists"

run_command "creating Raintale GUI tarball" "tar -C ${CLI_SRC_DIR} -c -v -z -f ${CLI_SRC_DIR}/dist/raintale-gui-${normalized_raintale_version}.tar.gz raintale-gui"

run_command "verifying Raintale GUI tarball" "ls ${CLI_SRC_DIR}/dist/raintale-gui-${normalized_raintale_version}.tar.gz" "nonewline"
echo " --- ${CLI_SRC_DIR}/dist/raintale-gui-${normalized_raintale_version}.tar.gz exists"

run_command "copying install script to archive directory" "cp ${CLI_SRC_DIR}/raintale-gui/installer/linux/raintale-install-script.sh ${CLI_SRC_DIR}/dist"
run_command "setting install script permissions" "chmod 0755 ${CLI_SRC_DIR}/raintale-gui/installer/linux/raintale-install-script.sh"

run_command "creating directory for installer" "mkdir -p ${CLI_SRC_DIR}/installer/generic-unix"

run_command "executing makeself" "makeself ${CLI_SRC_DIR}/dist/ ${CLI_SRC_DIR}/installer/generic-unix/install-raintale.sh 'Raintale from the Dark and Stormy Archives Project' ./raintale-install-script.sh"
installer_file=`cat ${command_output_file} | grep "successfully created" | sed 's/Self-extractable archive "//g' | sed 's/" successfully created.//g'`
echo "DONE: installer available at in ${installer_file}"
