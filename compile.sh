#!/bin/bash
# compile.sh
# GusE 2013-01-27 V1.0
#
# Compresses source files into the project file

EXE=project-create.py

for filename in templates/*; do
    name=$(basename $filename)
    contents=`python -c "import re; print open('$filename', 'r').read().encode('base64').replace('\n', '')"`
    sed -i "s|^FILES\['$name'\]='''.*'''$|FILES\['$name'\]='''$contents'''|g" $EXE
done

#TODO: this file should also update the create-project.info version number