#!/usr/bin/env sh

rm database.db
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
