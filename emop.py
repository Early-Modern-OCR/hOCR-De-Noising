#!/usr/bin/env python

import optparse
import os

from emop.emop_query import EmopQuery
from emop.emop_submit import EmopSubmit
from emop.emop_run import EmopRun
from emop.emop_upload import EmopUpload

# Needed to prevent the _JAVA_OPTIONS value from breaking some of
# the post processes that use Java
if os.environ.get("_JAVA_OPTIONS"):
    del os.environ["_JAVA_OPTIONS"]

# Define defaults and values used for command line options
default_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
mandatory_opts = ['mode']
modes = ['check', 'submit', 'run', 'upload']

# Define command line options
parser = optparse.OptionParser()
mandatory_opt_grp = optparse.OptionGroup(parser, "Mandatory Options")
common_opt_grp = optparse.OptionGroup(parser, "Common Options")
submit_opt_grp = optparse.OptionGroup(parser, "Submit Options")
run_opt_grp = optparse.OptionGroup(parser, "Run Options")
upload_opt_grp = optparse.OptionGroup(parser, "Upload Options")

mandatory_opt_grp.add_option('-m', '--mode',
                             type='choice',
                             help='Modes of operation. Choices: %s' % ", ".join(modes),
                             dest='mode',
                             action='store',
                             choices=modes,
                             nargs=1)
common_opt_grp.add_option('-c', '--config',
                          help='path to config.ini',
                          dest='config_path',
                          action='store',
                          default=default_config_path,
                          nargs=1,
                          type='string')
submit_opt_grp.add_option('--pages-per-job',
                          help='number of pages per job',
                          dest='pages_per_job',
                          action='store',
                          nargs=1,
                          type='int')
submit_opt_grp.add_option('--num-jobs',
                          help='number jobs to submit',
                          dest='num_jobs',
                          action='store',
                          nargs=1,
                          type='int')
common_opt_grp.add_option('--proc-id',
                          help='job proc-id',
                          dest='proc_id',
                          action='store',
                          nargs=1,
                          type='int')
upload_opt_grp.add_option('--upload-file',
                          help='path to payload file to upload',
                          dest='upload_file',
                          action='store',
                          nargs=1,
                          type='string')
upload_opt_grp.add_option('--upload-dir',
                          help='path to payload directory to upload',
                          dest='upload_dir',
                          action='store',
                          nargs=1,
                          type='string')

parser.add_option_group(mandatory_opt_grp)
parser.add_option_group(common_opt_grp)
parser.add_option_group(submit_opt_grp)
# parser.add_option_group(run_opt_grp)
parser.add_option_group(upload_opt_grp)
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

# Ensure upload mode was given at least --upload-file or --upload-dir
if opts.mode == 'upload' and not opts.upload_file and not opts.upload_dir and not opts.proc_id:
    print "Mode upload requires either --upload-file or --upload-dir"
    parser.print_help()
    exit(1)

# Ensure --upload-file and --upload-dir aren't used together
if ((opts.upload_file and opts.upload_dir) or
        (opts.upload_file and opts.proc_id) or
        (opts.upload_dir and opts.proc_id)):
    print "--proc-id, --upload-file, and --upload-dir can not be used together"
    parser.print_help()
    exit(1)

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
elif opts.mode == 'upload':
    emop_upload = EmopUpload(opts.config_path)
    if opts.proc_id:
        upload_status = emop_upload.upload_proc_id(proc_id=opts.proc_id)
    elif opts.upload_file:
        upload_status = emop_upload.upload_file(filename=opts.upload_file)
    elif opts.upload_dir:
        upload_status = emop_upload.upload_dir(dirname=opts.upload_dir)
