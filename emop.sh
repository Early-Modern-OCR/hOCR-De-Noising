#!/bin/bash

export _JAVA_OPTIONS="-Xmx32m -Xms16m"

DEBUG=0
VERBOSE=0
QUIET=0
NOOP=0
TEST=0
PAGES_PER_JOB=0
NUM_JOBS=0

SCRIPT_NAME=$(basename $0)

usage () {

cat << EOF
usage: ${SCRIPT_NAME} [OPTIONS]

This script submits emop.pbs jobs to the Torque resource manager.

ARGUMENTS:
  None

OPTIONS:

  -h, --help          Show this message.
  -d, --debug         Show debug output.
  -v, --verbose       Show progress messages.
  -q, --quiet         Supress all output.
  -n, --noop          Script runs without submitting jobs to Torque.
  -t, --test          Run script in noop mode and test various scenarios
                      testing 'division of labor'.
  --pages-per-job=N   Defaults to 0 which lets the script determine the optimal number
  --num-jobs=N        Defaults to 0 which lets the script determine the optimal number

EXAMPLE:

Run script with minimal output

  ${SCRIPT_NAME}

Run script without submitting a job and viewing verbose output

  ${SCRIPT_NAME} --noop --verbose

EOF
}

ARGS=`getopt -o hdvqnt -l help,debug,verbose,quiet,noop,test,pages-per-job:,num-jobs: -n "$0" -- "$@"`

[ $? -ne 0 ] && { usage; exit 1; }

eval set -- "${ARGS}"

while true; do
  case "$1" in
    -h|--help) usage ; exit 0 ;;
    -d|--debug) DEBUG=1 ; shift ;;
    -v|--verbose) VERBOSE=1 ; shift ;;
    -q|--quiet) QUIET=1 ; shift ;;
    -n|--noop) NOOP=1 ; shift ;;
    -t|--test) NOOP=1 ; TEST=1 ; shift ;;
    --pages-per-job) PAGES_PER_JOB=$2 ; shift 2 ;;
    --num-jobs) NUM_JOBS=$2 ; shift 2 ;;
    --) shift ; break ;;
    *) break ;;
  esac
done

[ $DEBUG -eq 1 ] && set -x
[ $QUIET -eq 1 ] && exec 1>/dev/null

export PATH=$PATH:/usr/local/bin

# this script lives in the root directory of the emop controller
# be sure to cd to this directory no matter how the script was 
# launched 
cd $(dirname $0)
export EMOP_HOME=$(pwd)
APP_NAME="emop-controller"

[ -f ${EMOP_HOME}/emop.conf ] && source ${EMOP_HOME}/emop.conf

LOGDIR=${LOGDIR-${EMOP_HOME}/logs}
LOGFILE="${LOGDIR}/${APP_NAME}-%j.out"

PARTITION="idhmc"
PARTITION_LIMIT=128
TOTAL_PAGES_TO_RUN=0
AVG_PAGE_RUNTIME=20
MIN_JOB_RUNTIME=300
MAX_JOB_RUNTIME=3600
PARTITION_TOTAL=`squeue -r --noheader -p ${PARTITION} -n ${APP_NAME} | wc -l`
PARTITION_AVAIL=`echo "$PARTITION_LIMIT - $PARTITION_TOTAL"|bc`

[ $NOOP -eq 1 ] && NOOP_PREFIX="(NOOP) " || NOOP_PREFIX=""

PAGE_CNT=0
JOBID=0

echo_verbose() {
  local msg="$1"
  if [ $VERBOSE -eq 1 ]; then
    echo $msg
  fi
}

ensure_environment() {
  if [ ! -d $LOGDIR ]; then
    echo_verbose "Creating LOGDIR: ${LOGDIR}"
    mkdir -p ${LOGDIR}
  fi
}

# ensure that there is work to do before scheduling
check_page_cnt() {
  PAGE_CNT=$(java -jar emop-controller.jar -mode check 2>/dev/null)
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

# only allow 128 emop_controller jobs to be scheduled at a time
check_partition_limit() {
  if [ $PARTITION_TOTAL -ge $PARTITION_LIMIT ];then
    echo "${PARTITION_LIMIT} instances of ${APP_NAME} is already running."
    exit 1
  fi
}

# Script to execute scancel
cancel_job() {
  local id=$1

  echo "Deleting queued job ${id}"
  CANCEL_CMD="scancel ${id}"
  echo_verbose "Executing: ${CANCEL_CMD}"
  eval $CANCEL_CMD
  exit 1
}

# there is work in the emop job_queue. Schedule the controller to process these jobs
submit_job() {
  local numpages=$1
  local jobID=0
  # Set a delay of 1 minute for all jobs to allow reservation to complete
  SUBMIT_CMD="sbatch --parsable --begin=now+60 -p ${PARTITION} -J ${APP_NAME} -o ${LOGFILE} emop.slrm"

  echo_verbose "${NOOP_PREFIX}Executing: ${SUBMIT_CMD}"
  if [ $NOOP -eq 0 ]; then
    jobID=`eval $SUBMIT_CMD`
    [ $? -ne 0 ] && { echo "sbatch command failed" ; exit 1; }
  else
    return
  fi

  JOB_RESERVED_CNT=$(java -jar emop-controller.jar -mode reserve -procid $jobID -numpages $numpages 2>/dev/null)
  # If the reservation fails, delete the job that was just submitted
  if [ $? -ne 0 ]; then
    echo "Failed to reserve ${numpages} pages for jobID: ${jobID}"
    cancel_job $jobID
  fi

  # If the return value from the reservation is not
  # the number of jobs to be reserved then qdel the job
  if [ $JOB_RESERVED_CNT -ne $numpages ]; then
    echo "Reserved count ${JOB_RESERVED_CNT} does not equal ${numpages}"
    cancel_job $jobID
  fi
}

# Optimize pages per job based on maximum and minimum job runtimes
optimize() {
  runOptionA=`echo "$PAGE_CNT / $PARTITION_AVAIL"|bc`
  runOptionB=`echo "$MAX_JOB_RUNTIME / $AVG_PAGE_RUNTIME"|bc`
  runOptionC=`echo "$MIN_JOB_RUNTIME / $AVG_PAGE_RUNTIME"|bc`

  if [ $runOptionA -gt $runOptionB ]; then
    NUM_JOBS=$PARTITION_AVAIL
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

  TOTAL_PAGES_TO_RUN=$((NUM_JOBS * PAGES_PER_JOB))

  echo "Optimal submission is ${NUM_JOBS} jobs with ${PAGES_PER_JOB} pages per job"
}

# This is a sort of regression test for efficiently diving up pages across jobs
local_test() {
  for pagecnt in 5 75 128 500 1280 128000; do
    PAGE_CNT=$pagecnt
    for qavail in 1 10 30 50 75 128; do
      PARTITION_AVAIL=$qavail
      echo "## TEST PARTITION_AVAIL ${PARTITION_AVAIL} | PAGE_CNT ${PAGE_CNT} ##"
      optimize
      
      if [ $NUM_JOBS -eq 0 ] || [ $NUM_JOBS -gt $PARTITION_LIMIT ]; then
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

# Run commands to ensure various necessary
# directories and paths exist
ensure_environment

# Check queue limits
check_partition_limit
echo_verbose "Available queue slots: ${PARTITION_AVAIL}"

# Check if actual pages to OCR
check_page_cnt
echo_verbose "Page count: ${PAGE_CNT}"

# Run optimization function
if [ $PAGES_PER_JOB -eq 0 -a $NUM_JOBS -eq 0 ]; then
  optimize
fi

echo "${NOOP_PREFIX}Executing ${NUM_JOBS} jobs with ${PAGES_PER_JOB} pages per job"
if [ $NOOP -eq 0 ]; then
  for i in $(seq 1 $NUM_JOBS); do
    submit_job $PAGES_PER_JOB
  done
fi

if [ $PAGES_PER_JOB -eq 0 -a $NUM_JOBS -eq 0 ]; then
  if [ $PAGE_CNT -gt $TOTAL_PAGES_TO_RUN ] && [ $NUM_JOBS -lt $PARTITION_AVAIL ]; then
    PAGES_REMAINDER=`echo "$PAGE_CNT - $TOTAL_PAGES_TO_RUN"|bc`
    echo "${NOOP_PREFIX}Executing 1 job with ${PAGES_REMAINDER} pages"
    [ $NOOP -eq 0 ] && submit_job $PAGES_REMAINDER
  fi
fi

exit 0
