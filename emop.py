#!/usr/bin/env python

import optparse
import os

from emop.emop_query import EmopQuery
from emop.emop_submit import EmopSubmit
from emop.emop_run import EmopRun

# Needed to prevent the _JAVA_OPTIONS value from breaking some of
# the post processes that use Java
if os.environ.get("_JAVA_OPTIONS"):
    del os.environ["_JAVA_OPTIONS"]

# Define defaults and values used for command line options
default_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
mandatory_opts = ['mode']
modes = ['check', 'submit', 'run']

# Define command line options
parser = optparse.OptionParser()
parser.add_option('-m', '--mode',
                  type='choice',
                  help='Modes of operation. Choices: %s' % ", ".join(modes),
                  dest='mode',
                  action='store',
                  choices=modes,
                  nargs=1)
parser.add_option('-c', '--config',
                  help='path to config.ini',
                  dest='config_path',
                  action='store',
                  default=default_config_path,
                  nargs=1,
                  type='string')
parser.add_option('--pages-per-job',
                  help='number of pages per job',
                  dest='pages_per_job',
                  action='store',
                  nargs=1,
                  type='int')
parser.add_option('--num-jobs',
                  help='number jobs to submit',
                  dest='num_jobs',
                  action='store',
                  nargs=1,
                  type='int')
parser.add_option('--proc-id',
                  help='job proc-id used when mode is run',
                  dest='proc_id',
                  action='store',
                  nargs=1,
                  type='int')

(opts, args) = parser.parse_args()

# Option validation
# Check for mandatory arguments
for m in mandatory_opts:
    if not opts.__dict__[m]:
        print "Must provide the %s option" % m
        parser.print_help()
        exit(-1)

# Ensure --num-jobs and --pages-per-job are both present
# if either is used
if (opts.num_jobs and not opts.pages_per_job
        or not opts.num_jobs and opts.pages_per_job):
    print "--num-jobs and --pages-per-job must be used together"
    parser.print_help()
    exit(-1)

# Ensure mode=run also has --proc-id
if opts.mode == 'run' and not opts.proc_id:
    print "--mode run requires --proc-id"
    parser.print_help()
    exit(-1)

# Perform actions based on the mode
# CHECK
if opts.mode == 'check':
    emop_query = EmopQuery(opts.config_path)
    pending_pages = emop_query.pending_pages()
    print "Number of pending pages: %s" % pending_pages
# SUBMIT
elif opts.mode == 'submit':
    emop_submit = EmopSubmit(opts.config_path)
    emop_query = EmopQuery(opts.config_path)
    pending_pages = emop_query.pending_pages()

    # Exit if no pages to run
    if pending_pages == 0:
        print "No work to be done"
        exit(0)

    # Exit if the number of submitted jobs has reached the limit
    current_job_count = emop_submit.current_job_count()
    if current_job_count >= emop_submit.settings.max_jobs:
        print "Job limit of %s reached." % emop_submit.settings.max_jobs
        exit(0)

    # Optimize job submission if --pages-per-job and --num-jobs was not set
    if not opts.pages_per_job and not opts.num_jobs:
        emop_submit.optimize_submit(pending_pages, current_job_count)
    else:
        emop_submit.num_jobs = opts.num_jobs
        emop_submit.pages_per_job = opts.pages_per_job

    # Loop that performs the actual submission
    for i in xrange(emop_submit.num_jobs):
        emop_submit.submit_job()
# RUN - this is typically done from compute node
elif opts.mode == 'run':
    emop_run = EmopRun(opts.config_path, opts.proc_id)
    run_status = emop_run.run()
