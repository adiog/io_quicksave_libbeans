#!/bin/bash
# This file is a part of quicksave project.
# Copyright 2017 Aleksander Gajewski <adiog@quicksave.io>.

cd $(dirname $0)

USER=$1
PASS=$2
KEY_FILE=$3
KEY_NAME=${4:-default}

USER_HASH=`echo -n "${USER}" | openssl sha1 -hmac "key" | cut -d" " -f2`
KEY_HASH=`cat ${KEY_FILE} | openssl sha1 -hmac "key" | cut -d" " -f2`

echo "INSERT INTO public.key (\"key_hash\", \"user_hash\", \"name\", \"value\") \
            VALUES('${KEY_HASH}', '${USER_HASH}', '${KEY_NAME}', '$(cat ${KEY_FILE})');"
