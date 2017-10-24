#!/usr/bin/env bash

cd $(dirname $0)

../sqlbeans/create_database_slave_sqlite_create_scripts.sh > db.ddl
../sqlbeans/create_database_master_sqlite_create_scripts.sh >> db.ddl
mkdir -p ../../../generated/qsgen/orm/
../../sqlpp11/scripts/ddl2cpp db.ddl ../../../generated/qsgen/orm/sqlppTables qs::orm
rm db.ddl
