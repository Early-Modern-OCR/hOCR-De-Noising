#!/bin/bash

DEBUG=0
VERBOSE=0
QUIET=0
NOOP=0
TEST=0

SCRIPT_NAME=$(basename $0)

usage () {

cat << EOF
usage: ${SCRIPT_NAME} [OPTIONS]

This script submits emop.pbs jobs to the Torque resource manager.

ARGUMENTS:
  None

OPTIONS:

  -h, --help      Show this message.
  -d, --debug     Show debug output.
  -v, --verbose   Show progress messages.
  -q, --quiet     Supress all output.
  -n, --noop      Script runs without submitting jobs to Torque.
  -t, --test      Run script in noop mode and test various scenarios
                  testing 'division of labor'.

EXAMPLE:

Run script with minimal output

  ${SCRIPT_NAME}

Run script without submitting a job and viewing verbose output

  ${SCRIPT_NAME} --noop --verbose

EOF
}

ARGS=`getopt -o hdvqnt -l help,debug,verbose,quiet,noop,test -n "$0" -- "$@"`

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
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -q|--quiet)
      QUIET=1
      shift
      ;;
    -n|--noop)
      NOOP=1
      shift
      ;;
    -t|--test)
      NOOP=1
      TEST=1
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

[ $DEBUG -eq 1 ] && set -x
[ $QUIET -eq 1 ] && exec 1>/dev/null

export PATH=$PATH:/usr/local/bin

# this script lives in the root directory of the emop controller
# be sure to cd to this directory no matter how the script was 
# launched 
cd $(dirname $0)
EMOP_HOME=$(pwd)
MODULES_SRC_DIR="${EMOP_HOME}/emop-modules/emop"
MODULES_DIR="${HOME}/privatemodules/emop"
HEAP_SIZE="128M"
APP_NAME="emop_controller"

Q="idhmc"
Q_LIMIT=128
NUM_JOBS=0
PAGES_PER_JOB=0
TOTAL_PAGES_TO_RUN=0
AVG_PAGE_RUNTIME=20
MIN_JOB_RUNTIME=300
MAX_JOB_RUNTIME=3600
Q_TOTAL=`qselect -q ${Q} -N ${APP_NAME} | wc -l`
Q_AVAIL=`echo "$Q_LIMIT - $Q_TOTAL"|bc`

[ $NOOP -eq 1 ] && NOOP_PREFIX="(NOOP) " || NOOP_PREFIX=""

PAGE_CNT=0
JOBID=0

echo_verbose() {
  local msg="$1"
  if [ $VERBOSE -eq 1 ]; then
    echo $msg
  fi
}

bootstrap_modules() {
  if [ ! -L $MODULES_DIR ]; then
    echo_verbose "${NOOP_PREFIX}Creating symbolic link ${MODULES_SRC_DIR} -> ${MODULES_DIR}"
    ln -sn ${MODULES_SRC_DIR} ${MODULES_DIR}
  fi
}

# ensure that there is work to do before scheduling
check_page_cnt() {
  PAGE_CNT=$(env EMOP_HOME=$EMOP_HOME java -Xms128M -Xmx128M -jar emop-controller.jar -mode check)
  if [ $? -ne 0 ];then
    # do not submit a new controller if there were  errors checking count
    echo "Unable to determine job count. Not launching eMOP controller"
    exit 1
  fi

  if [ $PAGE_CNT -eq 0 ]; then
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

# Script to execute qdel
qdel_job() {
  local id=$1

  echo "Deleting queued job ${id}"
  QDEL_CMD="qdel ${id}"
  echo_verbose "Executing: ${QDEL_CMD}"
  eval $QDEL_CMD
  exit 1
}

# there is work in the emop job_queue. Schedule the controller to process these jobs
qsub_job() {
  local numpages=$1
  local jobID=0
  # Set a delay of 1 minute for all jobs to allow reservation to complete
  local qsub_delay=$(date --date="-1 minutes ago" +%H%M)
  QSUB_CMD="qsub -a ${qsub_delay} -q ${Q} -N ${APP_NAME} -v EMOP_HOME='$EMOP_HOME',HEAP_SIZE='$HEAP_SIZE' -e $EMOP_HOME/logs -o $EMOP_HOME/logs emop.pbs"

  echo_verbose "${NOOP_PREFIX}Executing: ${QSUB_CMD}"
  if [ $NOOP -eq 0 ]; then
    qsub_return=`eval $QSUB_CMD`
    [ $? -ne 0 ] && { echo "qsub command failed" ; exit 1; }
    # Converts a jobid from [0-9].domain to [0-9]
    jobID="$(echo $qsub_return | cut -d'.' -f1)"
  else
    return
  fi

  JOB_RESERVED_CNT=$(env EMOP_HOME=$EMOP_HOME java -Xms128M -Xmx128M -jar emop-controller.jar -mode reserve -procid $jobID -numpages $numpages)
  # If the reservation fails, delete the job that was just submitted
  if [ $? -ne 0 ]; then
    echo "Failed to reserve ${numpages} pages for jobID: ${jobID}"
    qdel_job $jobID
  fi

  # If the return value from the reservation is not
  # the number of jobs to be reserved then qdel the job
  if [ $JOB_RESERVED_CNT -ne $numpages ]; then
    echo "Reserved count ${JOB_RESERVED_CNT} does not equal ${numpages}"
    qdel_job $jobID
  fi
}

# Optimize pages per job based on maximum and minimum job runtimes
optimize() {
  runOptionA=`echo "$PAGE_CNT / $Q_AVAIL"|bc`
  runOptionB=`echo "$MAX_JOB_RUNTIME / $AVG_PAGE_RUNTIME"|bc`
  runOptionC=`echo "$MIN_JOB_RUNTIME / $AVG_PAGE_RUNTIME"|bc`

  if [ $runOptionA -lt 1 ]; then
    NUM_JOBS=1
    PAGES_PER_JOB=$PAGE_CNT
  else
    if [ $runOptionA -gt $runOptionB ]; then
      NUM_JOBS=$Q_AVAIL
      PAGES_PER_JOB=$runOptionB
    elif [ $PAGE_CNT -lt $runOptionC ]; then
      NUM_JOBS=$((PAGE_CNT / runOptionC))
      PAGES_PER_JOB=$PAGE_CNT
    elif [ $runOptionA -lt $runOptionC ]; then
      NUM_JOBS=$((PAGE_CNT / runOptionC))
      PAGES_PER_JOB=$runOptionC
    else
      NUM_JOBS=$((PAGE_CNT / runOptionA))
      PAGES_PER_JOB=$runOptionA
    fi

    [ $NUM_JOBS -lt 1 ] && NUM_JOBS=1

    # Calculate expected runtime of a job based on average runtime
    expected_runtime=`echo "$PAGES_PER_JOB * $AVG_PAGE_RUNTIME"|bc`
    echo_verbose "Expected job runtime: ${expected_runtime} seconds"
  fi

  TOTAL_PAGES_TO_RUN=$((NUM_JOBS * PAGES_PER_JOB))

  echo "Optimal submission is ${NUM_JOBS} jobs with ${PAGES_PER_JOB} pages per job"
}

# This is a sort of regression test for efficiently diving up pages across jobs
local_test() {
  for pagecnt in 5 75 128 500 1280 128000; do
    PAGE_CNT=$pagecnt
    for qavail in 1 10 30 50 75 128; do
      Q_AVAIL=$qavail
      echo "## TEST Q_AVAIL ${Q_AVAIL} | PAGE_CNT ${PAGE_CNT} ##"
      optimize
      
      if [ $NUM_JOBS -eq 0 ] || [ $NUM_JOBS -gt $Q_LIMIT ]; then
        echo "## TEST FAILED | NUM_JOBS ${NUM_JOBS} | PAGES_PER_JOB ${PAGES_PER_JOB} ##"
        exit 1
      fi
    done
  done

  exit 0
}

if [ $TEST -eq 1 ]; then
  local_test
fi

# Bootstrap setup for jobs to run
bootstrap_modules

# Check queue limits
check_queue_limit
echo_verbose "Available queue slots: ${Q_AVAIL}"

# Check if actual pages to OCR
check_page_cnt
echo_verbose "Page count: ${PAGE_CNT}"

# Run optimization function
optimize

echo "${NOOP_PREFIX}Executing ${NUM_JOBS} jobs with ${PAGES_PER_JOB} pages per job"
if [ $NOOP -eq 0 ]; then
  for i in $(seq 1 $NUM_JOBS); do
    qsub_job $PAGES_PER_JOB
  done
fi

if [ $PAGE_CNT -gt $TOTAL_PAGES_TO_RUN ] && [ $NUM_JOBS -lt $Q_AVAIL ]; then
  PAGES_REMAINDER=`echo "$PAGE_CNT - $TOTAL_PAGES_TO_RUN"|bc`
  echo "${NOOP_PREFIX}Executing 1 job with ${PAGES_REMAINDER} pages"
  [ $NOOP -eq 0 ] && qsub_job $PAGES_REMAINDER
fi

exit 0
