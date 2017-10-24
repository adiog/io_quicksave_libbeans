#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

PYTHONPATH=..:$PYTHONPATH
INPUT=${1:-../../io_quicksave_beans}
OUTPUT=${2:-../../../generated}
shift 2
SPECIFIC_BEANS_ONLY=$*

OUTPUT_DIR=$OUTPUT/qsgen/abi
mkdir -p $OUTPUT_DIR

if [[ -z "$SPECIFIC_BEANS_ONLY" ]];
then
    BEANS=$(ls -1 $INPUT/*.json)
else
    for BEAN in $SPECIFIC_BEANS_ONLY;
    do
        BEANS="$BEANS $BEAN.json"
    done
fi

REFERENCE_FILE=${OUTPUT}/qsgen/ABI.h
echo "#pragma once" > ${REFERENCE_FILE}

for bean_file in $BEANS;
do
    BEAN=$(basename $bean_file);
    echo "Genarating $BEAN ..."
    BEAN_HEADER_FILENAME=${BEAN/.json/Bean.h}
    python3 generate.py $INPUT $BEAN | clang-format > $OUTPUT_DIR/${BEAN_HEADER_FILENAME}
    echo "... genarating $BEAN [DONE]"

    echo "#include <qsgen/abi/${BEAN_HEADER_FILENAME}>" >> ${REFERENCE_FILE}
done
