#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

GENERATOR=1-generate_orm_sqlpp_wrapper.py
IO_QUICKSAVE_BEANS_DIR=../../beans

OUTPUT_DIR=../../../generated/qsgen/orm/
mkdir -p ${OUTPUT_DIR}
OUTPUT_FILE=${OUTPUT_DIR}/sqlppWrappers.h
cp 1-generate_orm_sqlpp_template_header.h ${OUTPUT_FILE}

for bean in Meta; # File Action Tag Key Perspective;
do
  python3 ${GENERATOR} ${IO_QUICKSAVE_BEANS_DIR} ${bean}.json >> ${OUTPUT_FILE}
done

clang-format -i ${OUTPUT_FILE}
