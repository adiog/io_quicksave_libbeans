#!/usr/bin/env bash

cd $(dirname $0)

DB_USER=$1
DB_PASS=$2
KEY_FILE=$3
USER_HASH=`echo -n "$DB_USER" | openssl sha1 -hmac "key" | cut -d" " -f2`
DB_DATABASE=${4:-postgres://host=slave.quicksave.io port=5433 user=postgres}
DB_STORAGE=${5:-sshfs://host=storage.quicksave.io port=2222 key=default user=${USER} path=/home/${USER}}

echo "INSERT INTO public.user (\"user_hash\", \"username\", \"password\", \"databaseConnectionString\", \"storageConnectionString\") \
                        VALUES('${USER_HASH}', '${DB_USER}', '${DB_PASS}', '${DB_DATABASE}', '${DB_STORAGE}');"
