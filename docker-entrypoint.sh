#!/bin/bash
set -e

trap "kill -15 -1 && echo all proc killed" TERM KILL INT

if [ "$1" = "start" ]; then
	chown -R mysql:mysql /var/lib/mysql
	service mysql start
	mysql -uroot -e "CREATE DATABASE if not exists loonflownew DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
	mysql -uroot -e "CREATE USER loonflownew@127.0.0.1 IDENTIFIED BY '123456'";
	mysql -uroot -e "GRANT ALL PRIVILEGES ON loonflownew.* TO 'loonflownew'@'127.0.0.1';"
	mysql --one-database loonflownew < /opt/workflowdemo/loonflow.sql
	service redis-server start
	service nginx start
	service supervisor start
	sleep inf & wait
else
	exec "$@"
fi
