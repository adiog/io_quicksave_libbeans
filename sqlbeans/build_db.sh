#!/usr/bin/env bash

DB_FILE=${1:-db.sqlite3}
DB_USER=${2:-admin}
DB_PASS=${3:-admin}

GENERATOR=$IO_QUICKSAVE_BEANS_DIR/sqlbeans/generate.py
(
python3 $GENERATOR $IO_QUICKSAVE_QSBEANS_DIR User.json
python3 $GENERATOR $IO_QUICKSAVE_QSBEANS_DIR Session.json
python3 $GENERATOR $IO_QUICKSAVE_QSBEANS_DIR Item.json
python3 $GENERATOR $IO_QUICKSAVE_QSBEANS_DIR Tag.json
echo "INSERT INTO user VALUES(NULL, \"$DB_USER\", \"$DB_PASS\");"
) | sqlite3 $DB_FILE

