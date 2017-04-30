#!/usr/bin/env bash

cd $(dirname $0)

DATABASE_FILE=${1:-${IO_QUICKSAVE_DB_MASTER}}
DB_USER=${2:-${USER}}
USER_HASH=`echo -n "$DB_USER" | openssl sha1 -hmac "key" | cut -d" " -f2`
DB_PASS=${3:-${USER}}
DB_DATABASE=${4:-sqlite://${IO_QUICKSAVE_DB_SLAVE}}
DB_STORAGE=${5:-file://${IO_QUICKSAVE_CDN_DIR}/${USER_HASH}}
mkdir -p ${DB_STORAGE}
echo "INSERT INTO user (user_hash, username, password, databaseConnectionString, storageConnectionString) VALUES(\"${USER_HASH}\", \"${DB_USER}\", \"${DB_PASS}\", \"${DB_DATABASE}\", \"${DB_STORAGE}\");" | sqlite3 ${DATABASE_FILE}
