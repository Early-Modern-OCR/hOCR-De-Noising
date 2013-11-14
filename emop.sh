#!/bin/bash -x

export PATH=$PATH:/usr/local/bin

# this script lives in the root directory of the emop controller
# be sure to cd to this directory no matter how the script was 
# launched 
cd $(dirname $0)
EMOP_HOME=$(pwd)
HEAP_SIZE="128M"
APP_NAME="emop_controller"

Q="bgscrt"
Q_LIMIT=640
Q_TOTAL=`qselect -N ${APP_NAME} | wc -l`
Q_AVAIL=`echo "$Q_LIMIT - $Q_TOTAL"|bc`

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

# only allow 130 emop_controller jobs to be schedulated at a time
check_queue_limit() {
  if [ $Q_TOTAL -ge $Q_LIMIT ];then
    echo "${Q_LIMIT} instances of ${APP_NAME} is already running."
    exit 1
  fi
}

# there is work in the emop job_queue. Schedule the controller to process these jobs
# If more jobs exist in database than available brazos job slots, then fill up Brazos queue
qsub_job() {
  QSUB_CMD="qsub -q ${Q} -N ${APP_NAME} -v EMOP_HOME='$EMOP_HOME',HEAP_SIZE='$HEAP_SIZE' -e $EMOP_HOME/logs -o $EMOP_HOME/logs emop.pbs"

  if [ $JOB_CNT -gt $Q_AVAIL ]; then
    echo "Executing ${Q_AVAIL} times: ${QSUB_CMD}"
    for i in $(seq 1 $Q_AVAIL); do
      eval ${QSUB_CMD}
    done
  else
    echo "Executing: ${QSUB_CMD}"
    eval ${QSUB_CMD}
  fi
}

check_queue_limit
check_job_cnt
qsub_job

exit 0
