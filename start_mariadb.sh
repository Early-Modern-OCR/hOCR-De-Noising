#!/bin/bash

MY_CNF="${TMPDIR}/my.cnf"

LAUNCH_CMD="mysqld_safe --defaults-file=${MY_CNF} &>/dev/null &"
echo $LAUNCH_CMD
eval $LAUNCH_CMD

i=0
until `mysqladmin --defaults-file=${MY_CNF} ping 2>/dev/null | grep -q 'mysqld is alive'`
do
    echo "Waiting for MariaDB to start..."
    sleep 2
    if [ $i -ge 60 ]; then
      echo "MariaDB took over 1 minute to start, exiting."
      exit 1  
    fi
    i=$((i+1))
done

exit 0
