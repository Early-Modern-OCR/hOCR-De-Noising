#!/bin/bash

# this script lives in the root directory of the emop controller
# be sure to cd to this directory no matter how the script was 
# launched 
cd $(dirname $0)
EMOP_HOME=$(pwd)

APP_NAME="emop_controller"
CMD="qselect -N ${APP_NAME}"
Q_STATUS=$($CMD)

# only allow one emop controler to be schedulated at a time
if [ ! -z "$Q_STATUS" ]
then
   echo "An instance of ${APP_NAME} is already running."
   exit 1
else
   # ensure that there is work to do before scheduling
   JOB_CNT=$(env EMOP_HOME=$EMOP_HOME java -Xms128M -Xmx128M -jar emop-controller.jar -check)
   CODE=$?
   if [ $CODE -ne 0 ];
   then
      # do not submit a new controller if there were  errors checking count
      echo "Unable to determine job count. Not launching eMOP controller"
		exit 1
   else
      if [ $JOB_CNT -gt 0 ];
      then
         # there is work in the emop job_queue. Schedule the controller
         # to process these jobs
         qsub -v EMOP_HOME="${EMOP_HOME}" emop.pbs
      fi
   fi
fi

exit 0
