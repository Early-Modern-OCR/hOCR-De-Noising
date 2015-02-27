# eMOP Controller

[![Documentation Status](https://readthedocs.org/projects/emop-controller/badge/?version=latest)](https://readthedocs.org/projects/emop-controller/?badge=latest)
[![Build Status](https://travis-ci.org/idhmc-tamu/emop-controller.svg?branch=master)](https://travis-ci.org/idhmc-tamu/emop-controller)
[![Coverage Status](https://coveralls.io/repos/idhmc-tamu/emop-controller/badge.svg?branch=master)](https://coveralls.io/r/idhmc-tamu/emop-controller?branch=master)

The Brazos Cluster controller process for the eMOP workflow.

#### Table of Contents

1. [Install](#install)
2. [Build](#build)
3. [Setup](#setup)
4. [Usage](#usage)
  * [Query](#query)
  * [Submitting](#submitting)
  * [Uploading](#uploading)
  * [Test Run](#test-run)
  * [Cron](#cron)
5. [Support](#support)
6. [Development](#development)

## Install

Clone this repository and merge in the submodules

    git clone git@github.tamu.edu:emop/emop-controller.git
    cd emop-controller
    git submodule update --init

## Build

Step #1 is specific to the Brazos cluster and can be skipped if you have maven available.

1. Load emop-build module.

        module use ./modulefiles
        module load emop-build

2. Build and install all necessary dependencies.

        make all

3. Unload the emop-build module.

        module unload emop-build

## Setup

Depends on several environment variables as well. They are:

* TESSDATA_PREFIX - Path to the Tesseract training data
* JUXTA_HOME - Root directory for JuxtaCL
* RETAS_HOME - Root directory for RETAS
* SEASR_HOME - Root directory for SEASR post-processing tools
* DENOISE_HOME - Root directory for the DeNoise post-processing tool

For multiple users to run this controller on the same file structure the umask must be set to at least 002.

Add the following to your login scripts such as ~/.bashrc

    umask 002

Rename the following configuration files and change their values as needed:

* ~~emop.properties.example to emop.properties~~
* config.ini.example to config.ini

The file `config.ini` contains all the configuration options used by the emop-controller.

~~The file `emop.properties` is legacy and currently only used by the PageCorrector post-process.~~

## Usage

All interaction with the emop-controller is done through `emop.py`.  This script has a set of subcommands that determine the operations performed.

* query - form various queries against API and local files
* submit - submit jobs to the cluster
* run - run a job
* upload - upload completed job results
* testrun - Reserve, run and upload results.  Intended for testing.

For full list of options execute `emop.py --help` and `emop.py <subcommand> --help`.

Be sure the emop module is loaded before executing emop.py

    module use ./modulefiles
    module load emop

### Query

The following is an example of querying the dashboard API for count of pending pages (job_queues)

    ./emop.py query --pending-pages

This example will count pending pages (job_queues) that are part with batch_id 16

    ./emop.py query --filter '{"batch_id": 16}' --pending-pages

The log files can be queried for statistics of application runtimes.

    ./emop.py query --avg-runtimes

### Submitting

This is an example of submitting a single page to run in a single job:

    ./emop.py submit --num-jobs 1 --pages-per-job 1

This is an example of submitting and letting the emop-controller determine the optimal
number of jobs and pages-per-job to submit:

    ./emop.py submit

The `submit` subcommand can filter the jobs that get reserved via API by using the `--filter` argument.  The following example would reserve job_queues via API that match batch_id 16.

    ./emop.py submit --filter '{"batch_id": 16}'

### Uploading

This example is what is used to upload data from a SLURM job

    ./emop.py upload --proc-id 20141220211214811

This is an example of uploading a single file

    ./emop.py upload --upload-file payload/output/completed/20141220211214811.json

This is an example of uploading an entire directory

    ./emop.py upload --upload-dir payload/output/completed

### Test Run

The subcommand `testrun` is available so that small number of pages can be processed interactively
from within a cluster job.

First acquire an interactive job environment.  The following command is specific to Brazos and requests
an interactive job with 4000MB of memory.

    sintr -m 4000

Once the job starts and your on a compute node you can must load the emop modules.  These commands are also
specific to Brazos using Lmod.

    # Change to directory containing this project
    cd /path/to/emop-controller
    module use modulefiles
    module load emop

The following example will reserve 2 pages, process them and upload the results.

    ./emop.py testrun --num-pages 2

You can also run `testrun` with uploading of results disabled.

    ./emop.py testrun --num-pages 2 --no-upload

The same page can be reprocessed with a little bit of work.

First set the PROC_ID to the value that was output during the testrun:

    export PROC_ID=<some value>

Then use subcommand `run` with the PROC_ID of the previous run and `--force-run` to overwrite previous output.  This will read the input JSON file and allow the same page(s) to be processed

    ./emop.py run --force-run --proc-id ${PROC_ID}

### Cron

To submit jobs via cron a special wrapper script is provided

Edit cron by using `crontab -e` and add something like the following:

    EMOP_HOME=/path/to/emop-controller
    0 * * * * $EMOP_HOME/cron.sh config-cron.ini ; $EMOP_HOME/cron.sh config-cron-background.ini

The above example will execute two commands every hour.  The first launches `emop.py -c config-cron.ini submit` and the second launches `emop.py -c config-cron-background.ini submit`.

## Support

The use of this application relies heavily on sites using the following technologies

* SLURM - cluster resource manager
* Lmod - Modules environment

Only the following versions of each dependency have been tested.

* python-2.7.8
  * requests-2.5.0
  * subprocess32-3.2.6
* maven-3.2.1
* java-1.7.0-67
* tesseract - SVN revision 889

See `modulefiles/emop.lua` and `modulefiles/emop-build.lua` for a list of all the applications used

## Development

The following Python modules are needed for development

* flake8 - lint tests
* sphinx - docs creation

Install using the following

    pip install --user --requirement .requirements.txt

### Lint tests

Running lint tests

    flake8 --config config.ini .

### Documentation

Build documentation using Sphinx

    make docs

### System tests

To run the test using background-4g partition:

    sbatch -p background-4g tests/system/emop-ecco-test.slrm

Check the output of `logs/emop-controller-test-JOBID.out` where JOBID is the value output when sbatch was executed.
