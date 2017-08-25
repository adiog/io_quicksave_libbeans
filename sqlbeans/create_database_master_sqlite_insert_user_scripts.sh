#!/usr/bin/env bash

cd $(dirname $0)

DB_USER=${1:-adiog}
DB_PASS=${2:-pass}
USER_HASH=`echo -n "$DB_USER" | openssl sha1 -hmac "key" | cut -d" " -f2`
DB_DATABASE=${3:-sqlite:///io.quicksave.dev/adiog.db}
DB_STORAGE=${4:-file:///io.quicksave.dev/files/${DB_USER}}

echo "INSERT INTO user (\"user_hash\", \"username\", \"password\", \"databaseConnectionString\", \"storageConnectionString\") \
                  VALUES('${USER_HASH}', '${DB_USER}', '${DB_PASS}', '${DB_DATABASE}', '${DB_STORAGE}');"
