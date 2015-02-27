#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
NAME="emop-controller-cron"
EMOP_HOME=${EMOP_HOME:=$DIR}
LOCK_FILE="${EMOP_HOME}/.${NAME}.lock"
RETVAL=0

if [[ -n "$1" ]]; then
    CONFIG_ARG="-c $1"
else
    CONFIG_ARG=""
fi

{
    flock -x -n 200
    [ $? -ne 0 ] && { echo "Lock file ${LOCK_FILE} already exists"; exit 2; }

    . /etc/profile
    export EMOP_HOME=$EMOP_HOME
    cd $EMOP_HOME
    module use ${EMOP_HOME}/modulefiles
    module load emop
    python ${EMOP_HOME}/emop.py ${CONFIG_ARG} submit

} 200>${LOCK_FILE}

exit $RETVAL
