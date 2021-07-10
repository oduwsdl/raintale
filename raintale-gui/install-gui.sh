#!/bin/bash

if [ -z $VIRTUAL_ENV ]; then
    echo "It does not appear that you are installing Raintale's GUI inside a Python Virtualenv, quitting..."
    exit 255
fi

echo "Installing GUI inside environment at $VIRTUAL_ENV"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ -z "$1" ]; then
    WOOEY_DIR=${SCRIPT_DIR}/../raintale_with_wooey
else
    WOOEY_DIR=$1
fi

pip install . --use-feature=in-tree-build
pip install Django==3.1.8 # see https://github.com/wooey/Wooey/issues/334
pip install wooey

# create Wooey project
rm -rf ${WOOEY_DIR}

echo "creating Wooey project"
PROJECT_NAME=`basename ${WOOEY_DIR}`
cd `dirname ${WOOEY_DIR}`
wooify -p ${PROJECT_NAME}

echo "changing to ${WOOEY_DIR}"
cd ${WOOEY_DIR}

for script in `ls ${SCRIPT_DIR}/scripts/*.py`; do
    echo "adding script ${script}"
    python ./manage.py addscript "${script}"
done
