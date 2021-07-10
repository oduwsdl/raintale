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

PROJECT_NAME=`basename ${WOOEY_DIR}`
TEMPLATE_DIR=${WOOEY_DIR}/${PROJECT_NAME}/templates/wooey
STATIC_DIR=${WOOEY_DIR}/${PROJECT_NAME}/static
SETTINGS_DIR=${WOOEY_DIR}/${PROJECT_NAME}/settings
PARENT_DIR=`dirname ${WOOEY_DIR}`

pip freeze | grep raintale > /dev/null
status=$?

if [ $status -eq 0 ]; then
    echo "Raintale already installed, skipping install of Raintale"
else
    echo "installing Raintale"
    pip install . --use-feature=in-tree-build
fi

pip freeze | grep Django==3.1.8 > /dev/null
status=$?

if [ $status -eq 0 ]; then
    echo "Django already installed, skipping install of Django"
else
    echo "installing specific Django version"
    pip install Django==3.1.8 # see https://github.com/wooey/Wooey/issues/334
fi

pip freeze | grep wooey > /dev/null
status=$?

if [ $status -eq 0 ]; then
    echo "Wooey already installed, skipping install of Wooey"
else
    echo "installing Wooey"
    pip install wooey
fi

echo "clearing out old Wooey project, if any"
rm -rf ${WOOEY_DIR}

echo "creating clean Wooey project ${PROJECT_NAME} at ${PARENT_DIR}"
cd `dirname ${WOOEY_DIR}`
wooify -p ${PROJECT_NAME}

echo "installing templates into Django application at ${TEMPLATE_DIR}"
mkdir -p ${TEMPLATE_DIR}
cp -R ${SCRIPT_DIR}/templates/* ${TEMPLATE_DIR}

echo "installing static files (JS/CSS/images) into Django application at ${TEMPLATE_DIR}"
mkdir -p ${STATIC_DIR}
# cp ${SCRIPT_DIR}/static/js/* ${STATIC_DIR}/js/
cp ${SCRIPT_DIR}/static/css/* ${STATIC_DIR}/wooey/css/
cp ${SCRIPT_DIR}/static/images/* ${STATIC_DIR}/wooey/images/

echo "copying Django settings into Django application at ${WOOEY_DIR}"
cp ${SCRIPT_DIR}/settings/*.py ${SETTINGS_DIR}

echo "changing to ${WOOEY_DIR}"
cd ${WOOEY_DIR}

echo "adding scripts to Wooey"
oldIFS=$IFS
IFS='
'
for script in `ls ${SCRIPT_DIR}/scripts/*.py`; do
    echo "adding script ${script}"
    python ./manage.py addscript "${script}"
done
IFS=$oldIFS
