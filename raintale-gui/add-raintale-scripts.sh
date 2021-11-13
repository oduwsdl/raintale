#!/bin/bash

set -e

echo "adding Raintale scripts to Wooey"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../raintale_with_wooey"


python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Story From Template.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create HTML Story From Preset.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Tell Story With Twitter.py"
# python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Video Story.py"

echo "done adding Raintale scripts to Wooey"
