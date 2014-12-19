from emop.models.emop_page_result import EmopPageResult
from emop.models.emop_postproc_result import EmopPostprocResult


class EmopJob(object):

    def __init__(self, job_id, output_root_dir, image_path, batch_job, font, page, work, ground_truth_file, settings):
        self.id = job_id
        self.output_root_dir = output_root_dir
        self.image_path = image_path
        self.batch_job = batch_job
        self.font = font
        self.page = page
        self.work = work
        self.ground_truth_file = ground_truth_file
        self.settings = settings
        self.page_result = EmopPageResult()
        self.postproc_result = EmopPostprocResult()
        self.page_result.page_id = self.page.id
        self.page_result.batch_id = self.batch_job.id
        self.postproc_result.page_id = self.page.id
        self.postproc_result.batch_job_id = self.batch_job.id
        self.page_result.juxta_change_index = None
        self.page_result.alt_change_index = None
