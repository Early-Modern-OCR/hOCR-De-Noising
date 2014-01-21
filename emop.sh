#!/bin/bash

DEBUG=0
NOOP=0

usage () {

cat << EOF
usage: $(basename $0) [OPTIONS]

This script submits emop.pbs jobs to the Torque resource manager.

ARGUMENTS:
  None

OPTIONS:

  -h, --help      Show this message.
  -d, --debug     Show debug output.
  -n, --noop      Perform dry-run.
                  Script executes without submitting jobs to Torque.

EXAMPLE:

$(basename $0)

EOF
}

ARGS=`getopt -o hdn -l help,debug,noop -n "$0" -- "$@"`

[ $? -ne 0 ] && { usage; exit 1; }

eval set -- "${ARGS}"

while true; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -d|--debug)
      DEBUG=1
      shift
      ;;
    -n|--noop)
      NOOP=1
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if [ $DEBUG -eq 1 ]; then
  set -x
fi

export PATH=$PATH:/usr/local/bin

# this script lives in the root directory of the emop controller
# be sure to cd to this directory no matter how the script was 
# launched 
cd $(dirname $0)
EMOP_HOME=$(pwd)
HEAP_SIZE="128M"
APP_NAME="emop_controller"

Q="idhmc"
Q_LIMIT=128
Q_TOTAL=`qselect -q ${Q} -N ${APP_NAME} | wc -l`
Q_AVAIL=`echo "$Q_LIMIT - $Q_TOTAL"|bc`

[ $NOOP -eq 1 ] && NOOP_PREFIX="(NOOP) " || NOOP_PREFIX=""

JOB_CNT=0

# ensure that there is work to do before scheduling
check_job_cnt() {
  JOB_CNT=$(env EMOP_HOME=$EMOP_HOME java -Xms128M -Xmx128M -jar emop-controller.jar -check)
  CODE=$?
  if [ $CODE -ne 0 ];then
    # do not submit a new controller if there were  errors checking count
    echo "Unable to determine job count. Not launching eMOP controller"
    exit 1
  fi

  if [ $JOB_CNT -eq 0 ]; then
    echo "No work to be done"
    exit 0
  fi
}

# only allow 128 emop_controller jobs to be schedulated at a time
check_queue_limit() {
  if [ $Q_TOTAL -ge $Q_LIMIT ];then
    echo "${Q_LIMIT} instances of ${APP_NAME} is already running."
    exit 1
  fi
}

# there is work in the emop job_queue. Schedule the controller to process these jobs
qsub_job() {
  QSUB_CMD="qsub -q ${Q} -N ${APP_NAME} -v EMOP_HOME='$EMOP_HOME',HEAP_SIZE='$HEAP_SIZE' -e $EMOP_HOME/logs -o $EMOP_HOME/logs emop.pbs"

  echo "${NOOP_PREFIX}Executing: ${QSUB_CMD}"
  [ $NOOP -eq 0 ] && eval ${QSUB_CMD}
}

check_queue_limit
check_job_cnt
qsub_job

exit 0
