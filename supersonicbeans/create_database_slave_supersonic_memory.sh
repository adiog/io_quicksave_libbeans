#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

GENERATOR=generate_supersonic_memory.py
IO_QUICKSAVE_BEANS_DIR=../../beans

for bean in Meta File Action Tag Key Perspective;
do
  python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} ${bean}.json | clang-format > ../../../supersonic_quicksave/generated/SupersonicBean${bean}.h
done

