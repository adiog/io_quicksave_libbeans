#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

INPUT=$1
OUTPUT=$2
shift 2
SPECIFIC_BEANS_ONLY=$*

OUTPUT_DIR=$OUTPUT/generated/qsgen/databaseBean
mkdir -p $OUTPUT_DIR/sqlite

if [[ -z "$SPECIFIC_BEANS_ONLY" ]];
then
    BEANS=$(ls -1 $INPUT/*.json)
else
    for BEAN in $SPECIFIC_BEANS_ONLY;
    do
        BEANS="$BEANS $BEAN.json"
    done
fi

for bean_file in $BEANS;
do
    BEAN=$(basename $bean_file);
    echo "Genarating database $BEAN ..."
    python3 generate_sqlite.py $INPUT $BEAN | clang-format > $OUTPUT_DIR/sqlite/DatabaseBean${BEAN/.json/.h}
    echo "#include <qsgen/databaseBean/sqlite/DatabaseBean${BEAN/.json/.h}>" >> $OUTPUT_DIR/DatabaseBeans.h
    echo "... genarating database $BEAN [DONE]"
done
