from emop.lib.emop_base import EmopBase


class EmopQuery(EmopBase):

    def __init__(self, config_path):
        super(self.__class__, self).__init__(config_path)

    def pending_pages(self):
        job_status_params = {
            'name': 'Not Started',
        }
        job_status_request = self.emop_api.get_request("/api/job_statuses", job_status_params)
        if not job_status_request:
            return None
        job_status_results = job_status_request.get('results')[0]
        job_status_id = job_status_results.get('id')
        job_queue_params = {
            'job_status_id': "%s" % job_status_id,
        }
        job_queue_request = self.emop_api.get_request("/api/job_queues/count", job_queue_params)
        if not job_status_request:
            return None
        job_queue_results = job_queue_request.get('job_queue')
        count = job_queue_results.get('count')
        return count
