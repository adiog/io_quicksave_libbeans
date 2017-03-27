#!/usr/bin/env bash

cd $(dirname $0)

DATABASE_FILE=${1:-${IO_QUICKSAVE_DB_MASTER}}
BEANS_DIR=${2:-${IO_QUICKSAVE_BEANS_DIR}}

(
python3 generate_sqlite.py ${BEANS_DIR} User.json
) | sqlite3 ${DATABASE_FILE}
