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
        echo "the command '$command' is required to install Hypercane; it was not detected in your PATH"
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

    set -e
}

echo "Configuring Raintale WUI for Postgres database"
echo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

test_command "psql"

while test $# -gt 0; do

    case "$1" in
        --dbuser)
        shift
        DBUSER=$1
        echo "setting database username to ${DBUSER}"
        ;;
        --dbname)
        shift
        DBNAME=$1
        echo "setting database name to ${DBNAME}"
        ;;
        --dbhost)
        shift
        DBHOST=$1
        echo "setting database hostname to ${DBHOST}"
        ;;
        --dbport)
        shift
        DBPORT=$1
        echo "setting database port to ${DBPORT}"
        ;;
    esac
    shift

done

if [[ -z ${DBUSER} || -z ${DBNAME} || -z ${DBHOST} || -z ${DBPORT} ]]; then
    echo "Username, database name, database host, and database port are required."
    echo "You are missing one of the required arguments, please rerun with the missing value supplied. This is what I have:"
    echo "--dbuser ${DBUSER}"
    echo "--dbname ${DBNAME}"
    echo "--dbhost ${DBHOST}"
    echo "--dbport ${DBPORT}"
    echo
    exit 22 #EINVAL
fi

if [ -z ${DBPASSWORD} ]; then
    echo "please type the database password:"
    read -s DBPASSWORD
fi

echo "testing database connection"

echo "" | psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME}
status=$?

if [ ${status} -ne 0 ]; then
    echo "There was an issue connecting to 'postgresql://${DBUSER}:${DBHOST}:${DBPORT}/${DBNAME}', please verify the supplied database information."
fi

echo "verifying that database is empty"
export PGPASSWORD="${DBPASSWORD}"

tablecount=`echo "\dS" | psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME} | grep -P "^[ ]+public" | grep "| table" | wc -l | tr -d '[:space:]'`

echo "discovered $tablecount tables in the database"

if [ $tablecount != 0 ]; then
    echo "This script is meant to be run for a new empty database. The database at 'postgresql://${DBHOST}:${DBPORT}/${DBNAME}' contains tables from a previous install. Please drop the tables or specify a different database."
    exit
else
    echo "database is empty, continuing"
fi

settings_file=${WOOEY_DIR}/hypercane_with_wooey/settings/user_settings.py
raintale_conf=/etc/raintale.conf

echo "writing database information to ${settings_file}"

ME_line=`grep MEMENTOEMBED_ENDPOINT`

cat >> ${raintale_conf} <<- EOF
${ME_line}
DATABASE_NAME="${DBNAME}"
DATABASE_PORT="${DBPORT}"
DATABASE_HOST="${DBHOST}"
DATABASE_USER="${DBUSER}"
DATABASE_PASSWORD="${DBPASSWORD}"
EOF

cat >> ${settings_file} <<- EOF
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'raintale'),
        'USER': os.environ.get('DATABASE_USER', 'raintale'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'raintale_password'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432')
    }
}
EOF

echo "creating database schema"
startdir=`pwd`
echo "changing to ${WOOEY_DIR}"
cd ${WOOEY_DIR}
python ./manage.py migrate
cd ${startdir}

echo "updating schema at database ${DBNAME} for defects"

psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME} <<EOF
ALTER TABLE wooey_scriptversion ALTER COLUMN script_path TYPE varchar(255);
CREATE TABLE IF NOT EXISTS "wooey_cache_table" (
    "cache_key" VARCHAR(255) NOT NULL PRIMARY KEY,
    "value" TEXT NOT NULL,
    "expires" TIMESTAMP NOT NULL
);
ALTER TABLE "wooey_cache_table" OWNER TO ${DBUSER}
EOF

# add Hypercane scripts
"${SCRIPT_DIR}/add-raintale-scripts.sh"

echo
echo "You must restart the Raintale WUI service to start using the queueing service"
echo
echo "Done configuring Raintale for Postgres"
