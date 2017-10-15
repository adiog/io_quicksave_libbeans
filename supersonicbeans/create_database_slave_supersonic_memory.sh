#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

GENERATOR=generate_supersonic_memory.py
IO_QUICKSAVE_BEANS_DIR=../../io_quicksave_beans

(
python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Meta.json
#python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} File.json
#python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Action.json
#python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Tag.json
#python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Key.json
#python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} Perspective.json
) #| clang-format
