#!/usr/bin/env bash

cd $(dirname $0)

GENERATOR=generate_postgres.py

python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} User.json

