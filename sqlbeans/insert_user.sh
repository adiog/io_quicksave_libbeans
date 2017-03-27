#!/usr/bin/env bash

cd $(dirname $0)

DATABASE_FILE=${1:-${IO_QUICKSAVE_DB_MASTER}}
DB_USER=${2:-${USER}}
DB_PASS=${3:-${USER}}
DB_PRIVATE=${4:-${IO_QUICKSAVE_DB_PRIVATE}}
DB_FILESYSTEM=${5:-${IO_QUICKSAVE_CDN_DIR}/${DB_USER}}
USER_HASH=`echo -n "$DB_USER" | openssl sha1 -hmac "key" | cut -d" " -f2`
echo "INSERT INTO user (user_hash, username, password, databaseConnectionString, filesystemConnectionString) VALUES(\"${USER_HASH}\", \"${DB_USER}\", \"${DB_PASS}\", \"${DB_PRIVATE}\", \"${DB_FILESYSTEM}\");" | sqlite3 ${DATABASE_FILE}
