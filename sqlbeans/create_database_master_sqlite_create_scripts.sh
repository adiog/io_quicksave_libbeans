#!/usr/bin/env bash

cd $(dirname $0)

GENERATOR=generate_sqlite.py

python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} User.json

