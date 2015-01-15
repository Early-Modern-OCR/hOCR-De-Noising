#!/bin/bash

ERROR_COUNT=$(grep -HnR "ERROR:" logs/emop-controller-*.out | wc -l)
WALLTIME_ERROR_COUNT=$(grep -HnR "TIME LIMIT" logs/*.out | wc -l)

bootstrap_total=0
bootstrap_count=0
for i in $(grep "BOOTSTRAP TIME:" logs/*.out | awk '{ print $3; }'); do
    bootstrap_total=$(echo $bootstrap_total+$i | bc)
    ((bootstrap_count++))
done
BOOTSTRAP_AVG=$(echo "scale=2; $bootstrap_total / $bootstrap_count" | bc)

start_mariadb_total=0
start_mariadb_count=0
for i in $(grep "START MARIADB TIME:" logs/*.out | awk '{ print $4; }'); do
    start_mariadb_total=$(echo $start_mariadb_total+$i | bc)
    ((start_mariadb_count++))
done
START_MARIADB_AVG=$(echo "scale=2; $start_mariadb_total / $start_mariadb_count" | bc)

./emop.py --mode query --avg-runtimes

echo "ERROR COUNT: ${ERROR_COUNT}"
echo "HIT WALLTIME LIMIT COUNT: ${WALLTIME_ERROR_COUNT}"

echo "BOOTSTRAP AVG TIME: ${BOOTSTRAP_AVG}"
echo "START MARIADB AVG TIME: ${START_MARIADB_AVG}"
