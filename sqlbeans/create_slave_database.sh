#!/usr/bin/env bash

cd $(dirname $0)

DB_SLAVE=${1:-${IO_QUICKSAVE_DB_SLAVE}}
BEANS_DIR=${2:-${IO_QUICKSAVE_BEANS_DIR}}

GENERATOR=
(
python3 generate_sqlite.py ${BEANS_DIR} Meta.json
python3 generate_sqlite.py ${BEANS_DIR} File.json
python3 generate_sqlite.py ${BEANS_DIR} Action.json
python3 generate_sqlite.py ${BEANS_DIR} Tag.json
python3 generate_sqlite.py ${BEANS_DIR} User.json
) | sqlite3 $DB_SLAVE
