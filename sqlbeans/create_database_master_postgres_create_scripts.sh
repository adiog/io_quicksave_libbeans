#!/usr/bin/env bash

cd $(dirname $0)

GENERATOR=generate_postgres.py

python3 ${GENERATOR} ../../io_quicksave_beans User.json

