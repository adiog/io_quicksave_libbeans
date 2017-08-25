#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

GENERATOR=generate_sqlite.py
SCHEMA=${1:-public}

(
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Meta.json $SCHEMA
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} File.json $SCHEMA
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Action.json $SCHEMA
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Tag.json $SCHEMA
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Key.json $SCHEMA
) | sed -e 's# REFERENCES "user" ("user_hash")##'
