#!/usr/bin/env bash

cd $(dirname $0)

GENERATOR=generate_sqlite.py

python3 ${GENERATOR} ../../io_quicksave_beans User.json
