#!/bin/bash

# Update version in project
VERSION_STRING=`date -u +0.%Y.%m.%d.%H%M%S`
FILE_NAME='raintale/version.py'
DOC_FILE_NAME='docs/source/conf.py'

# Update Raintale version
sed -i.bak "s/^__appversion__ = .*$/__appversion__ = '$VERSION_STRING'/g" $FILE_NAME
rm $FILE_NAME.bak
sed -i.bak "s/^release = u'.*'$/release = u'$VERSION_STRING'/g" $DOC_FILE_NAME
rm $DOC_FILE_NAME.bak
