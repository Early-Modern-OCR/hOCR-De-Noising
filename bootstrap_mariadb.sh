#!/bin/bash

# Setup #

# sintr -m 4000
# module load gcc mariadb
# mysql_install_db --basedir=${BRAZOS_MARIADB_ROOT} --defaults-file=${TMPDIR}/my.cnf
# nohup mysqld_safe --defaults-file=${TMPDIR}/my.cnf --innodb_fast_shutdown=0 --innodb_change_buffering=none &
# mysql --defaults-file=${TMPDIR}/my.cnf -e 'CREATE DATABASE google_1grams DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
# mysql --defaults-file=${TMPDIR}/my.cnf google_1grams < /dh/data/shared/db-backups/google_1grams.sql

# mysql --defaults-file=${TMPDIR}/my.cnf google_1grams < /dh/data/shared/db-backups/google_1grams/ngram3_lower.sql
# 
# 

# for file in /dh/data/shared/db-backups/google_1grams/chunks/ngram3_lower_* ; do  echo $file ; mysql --defaults-file=${TMPDIR}/my.cnf google_1grams -e "LOAD DATA INFILE '$file' INTO TABLE ngram3_lower"; done

# mysqladmin --defaults-file=${TMPDIR}/my.cnf --protocol=tcp shutdown

#########

MY_CNF="${TMPDIR}/my.cnf"
ROOT_DIR="${TMPDIR}/mariadb"
TMP_DIR="${ROOT_DIR}/tmp"
#DATA_DIR="${ROOT_DIR}/data"
DATA_DIR="${ROOT_DIR}/data"
SRC="/fdata/idhmc/serial/google_1grams/data"
SOCKET="${ROOT_DIR}/mysql.sock"
PORT=60${SLURM_JOB_ID: -3} #TODO This is a huge assumption about value of SLURM_JOB_ID > 1000

cat << EOF > ${TMPDIR}/emop.properties
ctx_db_driver: com.mysql.jdbc.Driver
ctx_db_url: jdbc:mysql://127.0.0.1:${PORT}/google_1grams
ctx_db_user: root
ctx_db_pass:
EOF

cat << EOF  > ${MY_CNF}

[mysqld]
socket = $SOCKET
port = $PORT
basedir = $BRAZOS_MARIADB_ROOT
tmpdir = $TMP_DIR
datadir = $DATA_DIR
user = $USER
pid-file = ${TMPDIR}/mariadb-${SLURM_JOB_ID}.pid
#log-error = ${TMPDIR}/mariadb-${SLURM_JOB_ID}.err
log-error = /dh/data/shared/db-backups/mariadb/mariadb-${SLURM_JOB_ID}.err
log-warnings = 2

# From my-huge.cnf
skip-external-locking
key_buffer_size = 384M
max_allowed_packet = 1M
table_open_cache = 512
sort_buffer_size = 2M
read_buffer_size = 2M
read_rnd_buffer_size = 8M
myisam_sort_buffer_size = 64M
thread_cache_size = 8
query_cache_size = 32M
# Try number of CPU's*2 for thread_concurrency
thread_concurrency = 4

bind-address = 127.0.0.1
#skip-networking

default-storage-engine = InnoDB
innodb_data_home_dir = $DATA_DIR
innodb_data_file_path = ibdata1:2000M;ibdata2:10M:autoextend
innodb_log_group_home_dir = $DATA_DIR
# You can set .._buffer_pool_size up to 50 - 80 %
# of RAM but beware of setting memory usage too high
innodb_buffer_pool_size = 256M
innodb_additional_mem_pool_size = 20M
# Set .._log_file_size to 25 % of buffer pool size
innodb_log_file_size = 256M
innodb_log_buffer_size = 8M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50

# Make readonly
# Need MariaDB 10.0 for these
innodb_change_buffering = none
innodb_read_only = 1
event_scheduler = DISABLED

# Attempt to fix IO access issues when running on /fdata (BeeGFS)
innodb_use_native_aio = 0

#external-locking

[mysql]
no-auto-rehash

[client]
user = root
host = 127.0.0.1
#host = localhost
socket = $SOCKET
port = $PORT

EOF

[ -d $TMP_DIR ] || mkdir -p $TMP_DIR
[ -d $DATA_DIR ] || mkdir -p $DATA_DIR

rsync -a --exclude='ibdata2' --exclude='google_1grams' ${SRC} ${ROOT_DIR}/
ln -sfn ${SRC}/ibdata2 ${DATA_DIR}/ibdata2
ln -sfn ${SRC}/google_1grams ${DATA_DIR}/google_1grams

exit 0
