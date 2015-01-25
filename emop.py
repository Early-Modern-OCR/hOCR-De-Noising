#!/usr/bin/env python

import json
import argparse
import os
import sys

from emop.emop_query import EmopQuery
from emop.emop_submit import EmopSubmit
from emop.emop_run import EmopRun
from emop.emop_upload import EmopUpload

# Needed to prevent the _JAVA_OPTIONS value from breaking some of
# the post processes that use Java
if os.environ.get("_JAVA_OPTIONS"):
    del os.environ["_JAVA_OPTIONS"]


def query(args, parser):
    emop_query = EmopQuery(args.config_path)
    # --pending-pages
    if args.query_pending_pages:
        pending_pages = emop_query.pending_pages(q_filter=args.filter)
        if pending_pages == 0 or pending_pages:
            print "Number of pending pages: %s" % pending_pages
        else:
            print "ERROR: querying pending pages failed"
            sys.exit(1)
    # --avg-runtimes
    if args.query_avg_runtimes:
        avg_runtimes = emop_query.get_runtimes()
        if avg_runtimes:
            print "Pages completed: %d" % avg_runtimes["total_pages"]
            print "Total Page Runtime: %d seconds" % avg_runtimes["total_page_runtime"]
            print "Average Page Runtime: %d seconds" % avg_runtimes["average_page_runtime"]
            print "Jobs completed: %d" % avg_runtimes["total_jobs"]
            print "Average Job Runtime: %d seconds" % avg_runtimes["average_job_runtime"]
            print "Processes:"
            for process in avg_runtimes["processes"]:
                print "\t%s completed: %d" % (process["name"], process["count"])
                print "\t%s Average: %d seconds" % (process["name"], process["avg"])
                print "\t%s Total: %d seconds" % (process["name"], process["total"])
        else:
            print "ERROR: querying average page runtimes"
            sys.exit(1)
    sys.exit(0)


def submit(args, parser):
    """SUBMIT
    """
    # Ensure --num-jobs and --pages-per-job are both present
    # if either is used
    if (args.num_jobs and not args.pages_per_job
            or not args.num_jobs and args.pages_per_job):
        print "--num-jobs and --pages-per-job must be used together"
        parser.print_help()
        sys.exit(1)

    emop_submit = EmopSubmit(args.config_path)
    emop_query = EmopQuery(args.config_path)
    pending_pages = emop_query.pending_pages(q_filter=args.filter)

    # Exit if no pages to run
    if pending_pages == 0:
        print "No work to be done"
        sys.exit(0)

    if not pending_pages:
        print "Error querying pending pages"
        sys.exit(1)

    # Exit if the number of submitted jobs has reached the limit
    if args.schedule:
        current_job_count = emop_submit.scheduler.current_job_count()
        if current_job_count >= emop_submit.settings.max_jobs:
            print "Job limit of %s reached." % emop_submit.settings.max_jobs
            sys.exit(0)

    # Optimize job submission if --pages-per-job and --num-jobs was not set
    if not args.pages_per_job and not args.num_jobs:
        num_jobs, pages_per_job = emop_submit.optimize_submit(pending_pages, current_job_count, sim=args.submit_simulate)
    else:
        num_jobs = args.num_jobs
        pages_per_job = args.pages_per_job

    if args.submit_simulate:
        sys.exit(0)

    # Loop that performs the actual submission
    for i in xrange(num_jobs):
        proc_id = emop_submit.reserve(num_pages=pages_per_job, r_filter=args.filter)
        if not proc_id:
            print "Failed to reserve page"
            sys.exit(1)
        emop_submit.scheduler.submit_job(proc_id=proc_id, num_pages=pages_per_job)
    sys.exit(0)


def run(args, parser):
    """Run subcommand function

    This is done from a compute node
    """
    emop_run = EmopRun(args.config_path, args.proc_id)

    # Do not use run subcommand if not in a valid cluster job environment
    # This prevents accidentally running resource intensive program on login nodes
    if not emop_run.scheduler.is_job_environment():
        print "Can only use run subcommand from within a cluster job environment"
        sys.exit(1)
    run_status = emop_run.run(force=args.force_run)
    if run_status:
        sys.exit(0)
    else:
        sys.exit(1)


def upload(args, parser):
    """Upload
    """
    emop_upload = EmopUpload(args.config_path)
    if args.proc_id:
        upload_status = emop_upload.upload_proc_id(proc_id=args.proc_id)
    elif args.upload_file:
        upload_status = emop_upload.upload_file(filename=args.upload_file)
    elif args.upload_dir:
        upload_status = emop_upload.upload_dir(dirname=args.upload_dir)

    if upload_status:
        sys.exit(0)
    else:
        sys.exit(1)


def testrun(args, parser):
    """TESTRUN

    Reserve pages, run pages and optionally upload pages
    """
    emop_submit = EmopSubmit(args.config_path)

    # Do not run testrun subcommand if not in a valid cluster job environment
    # This prevents accidentally running resource intensive program on login nodes
    if not emop_submit.scheduler.is_job_environment():
        print "Can only use testrun subcommand from within a cluster job environment"
        sys.exit(1)

    # Reserve pages equal to --num-pages
    proc_id = emop_submit.reserve(num_pages=args.testrun_num_pages, r_filter=args.filter)
    if not proc_id:
        print "Failed to reserve pages"
        sys.exit(1)
    # Run reserved pages
    emop_run = EmopRun(args.config_path, proc_id)
    run_status = emop_run.run(force=True)
    if not run_status:
        sys.exit(1)

    # Exit if --no-upload
    if args.testrun_no_upload:
        sys.exit(0)
    # Upload results
    emop_upload = EmopUpload(args.config_path)
    upload_status = emop_upload.upload_proc_id(proc_id=proc_id)
    if not upload_status:
        sys.exit(1)

    sys.exit(0)


# Define defaults and values used for command line options
default_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')

# Define command line options
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='mode')
parser_query = subparsers.add_parser('query')
parser_submit = subparsers.add_parser('submit')
parser_run = subparsers.add_parser('run')
parser_upload = subparsers.add_parser('upload')
parser_testrun = subparsers.add_parser('testrun')

proc_id_args = '--proc-id',
proc_id_kwargs = {
    'help': 'job proc-id',
    'dest': 'proc_id',
    'action': 'store',
    'type': str
}
filter_args = '--filter',
filter_kwargs = {
    'help': 'filter to apply',
    'dest': 'filter',
    'action': 'store',
    'default': '{}',
    'type': json.loads
}

# Global config options
parser.add_argument('-c', '--config',
                    help="path to config file",
                    dest="config_path",
                    action="store",
                    default=default_config_path,
                    type=str)

# query args
parser_query.add_argument(*filter_args, **filter_kwargs)
parser_query.add_argument('--pending-pages',
                          help="query number of pending pages",
                          dest="query_pending_pages",
                          action="store_true")
parser_query.add_argument('--avg-runtimes',
                          help="query average runtimes of completed jobs",
                          dest="query_avg_runtimes",
                          action="store_true")
parser_query.set_defaults(func=query)
# submit args
parser_submit.add_argument(*filter_args, **filter_kwargs)
parser_submit.add_argument('--pages-per-job',
                           help='number of pages per job',
                           dest='pages_per_job',
                           action='store',
                           type=int)
parser_submit.add_argument('--num-jobs',
                           help='number jobs to submit',
                           dest='num_jobs',
                           action='store',
                           type=int)
parser_submit.add_argument('--sim',
                           help='simulate job submission',
                           dest='submit_simulate',
                           action='store_true')
parser_submit.add_argument('--no-schedule',
                           help='disable submitting to scheduler',
                           dest='schedule',
                           action='store_false',
                           default=True)
parser_submit.set_defaults(func=submit)
# run args
parser_run.add_argument(*proc_id_args, required=True, **proc_id_kwargs)
parser_run.add_argument('--force-run',
                        help='Force run even if output exists',
                        dest='force_run',
                        action='store_true')
parser_run.set_defaults(func=run)
# upload args
upload_group = parser_upload.add_mutually_exclusive_group(required=True)
upload_group.add_argument(*proc_id_args, **proc_id_kwargs)
upload_group.add_argument('--upload-file',
                          help='path to payload file to upload',
                          dest='upload_file',
                          action='store',
                          type=str)
upload_group.add_argument('--upload-dir',
                          help='path to payload directory to upload',
                          dest='upload_dir',
                          action='store',
                          type=str)
parser_upload.set_defaults(func=upload)
# testrun args
parser_testrun.add_argument(*filter_args, **filter_kwargs)
parser_testrun.add_argument('--num-pages',
                            help='number pages to reserve and run',
                            dest='testrun_num_pages',
                            action='store',
                            type=int,
                            default=1)
parser_testrun.add_argument('--no-upload',
                            help='disable uploading of results',
                            dest='testrun_no_upload',
                            action='store_true',
                            default=False)
parser_testrun.set_defaults(func=testrun)

args = parser.parse_args()
args.func(args, parser)
