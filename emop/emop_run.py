import json
import logging
from emop.lib.emop_base import EmopBase
from emop.lib.emop_payload import EmopPayload
from emop.lib.emop_job import EmopJob
from emop.models.emop_batch_job import EmopBatchJob
from emop.models.emop_font import EmopFont
from emop.models.emop_page import EmopPage
from emop.models.emop_work import EmopWork
from emop.lib.processes.tesseract import Tesseract
from emop.lib.processes.xml_to_text import XML_To_Text
from emop.lib.processes.denoise import Denoise
from emop.lib.processes.page_evaluator import PageEvaluator
from emop.lib.processes.page_corrector import PageCorrector
from emop.lib.processes.juxta_compare import JuxtaCompare
from emop.lib.processes.retas_compare import RetasCompare

logger = logging.getLogger('emop')


class EmopRun(EmopBase):

    def __init__(self, config_path, proc_id):
        super(self.__class__, self).__init__(config_path)
        self.proc_id = proc_id
        self.payload = EmopPayload(self.settings.payload_input_path, self.settings.payload_output_path, proc_id)
        self.results = {}
        self.jobs_completed = []
        self.jobs_failed = []
        self.page_results = []
        self.postproc_results = []

    def get_image_path(self, page, work):
        image_path = page.image_path
        if image_path:
            return EmopBase.add_prefix(self.settings.input_path_prefix, image_path)
        # image path was not provided by API so one will be generated
        else:
            if work.is_ecco():
                # ECCO format: ECCO number + 4 digit page + 0.tif
                img = "%s/%s%04d0.tif" % (work.ecco_directory, work.ecco_number, page.number)
                return img
            else:
                # EEBO format: 00014.000.001.tif where 00014 is the page number.
                # EEBO is a problem because of the last segment before .tif. It is some
                # kind of version info and can vary. Start with 0 and increase til
                # a file is found.
                # TODO
                return None

    def append_result(self, job, results, failed=False):
        if failed:
            logger.error(results)
            self.jobs_failed.append({"id": job.id, "results": results})
        else:
            self.jobs_completed.append(job.id)

        # TODO: Do we need to handle adding page_results and postproc_results differently??
        self.page_results.append(job.page_result.__dict__)
        self.postproc_results.append(job.postproc_result.__dict__)

    def do_process(self, obj, job, **kwargs):
        klass = obj.__class__.__name__
        result = obj.run(**kwargs)
        if result.exitcode != 0:
            err = "%s Failed: %s" % (klass, result.stderr)
            self.append_result(job=job, results=err, failed=True)
            return None
        else:
            return True

    @EmopBase.timing
    def do_ocr(self, batch_job, job):
        font = EmopFont()
        page = EmopPage()
        work = EmopWork()
        font.setattrs(job["batch_job"]["font"])
        page.setattrs(job["page"])
        work.setattrs(job["work"])
        # TODO adding prefix should be handled else where
        output_root_dir = EmopBase.add_prefix(self.settings.output_path_prefix, self.settings.ocr_root)
        image_path = self.get_image_path(page, work)
        # TODO adding prefix should be handled by EmopPage class
        ground_truth_file = EmopBase.add_prefix(self.settings.input_path_prefix, page.ground_truth_file)
        emop_job = EmopJob(job["id"], output_root_dir, image_path, batch_job, font, page, work, ground_truth_file)

        # TODO: Remove
        # print "PAGE: \n %s" % json.dumps(vars(page), sort_keys=True, indent=4)

        logger.info(
            "Got job [%s] - Batch: %s JobType: %s OCR Engine: %s" %
            (emop_job.id, emop_job.batch_job.name, emop_job.batch_job.job_type, emop_job.batch_job.ocr_engine)
        )

        # OCR #
        ocr_engine = emop_job.batch_job.ocr_engine
        if ocr_engine == "tesseract":
            ocr = Tesseract(job=emop_job)
            ocr_result = ocr.run()
        else:
            ocr_engine_err = "OCR with %s not yet supported" % ocr_engine
            self.append_result(job=emop_job, results=ocr_engine_err, failed=True)
            return

        if ocr_result.exitcode != 0:
            ocr_err = "OCR Failed: %s" % ocr_result.stderr
            self.append_result(job=emop_job, results=ocr_err, failed=True)
            return

        # DeNoise #
        denoise = Denoise(job=emop_job)
        denoise_proc = self.do_process(denoise, emop_job)
        if not denoise_proc:
            return

        # _IDHMC.xml to _IDHMC.txt #
        xml_to_text = XML_To_Text(job=emop_job)
        xml_to_text_proc = self.do_process(xml_to_text, emop_job)
        if not xml_to_text_proc:
            return

        # PageEvaluator #
        page_evaluator = PageEvaluator(job=emop_job)
        page_evaluator_proc = self.do_process(page_evaluator, emop_job)
        if not page_evaluator_proc:
            return

        # PageCorrector #
        page_corrector = PageCorrector(job=emop_job)
        page_corrector_proc = self.do_process(page_corrector, emop_job)
        if not page_corrector_proc:
            return

        # JuxtaCompare postprocess and OCR output #
        juxta_compare = JuxtaCompare(job=emop_job)
        juxta_compare_proc_pp = self.do_process(juxta_compare, emop_job, postproc=True)
        if not juxta_compare_proc_pp:
            return
        juxta_compare_proc = self.do_process(juxta_compare, emop_job, postproc=False)
        if not juxta_compare_proc:
            return

        # RetasCompare postprocess and OCR output #
        retas_compare = RetasCompare(job=emop_job)
        retas_compare_proc_pp = self.do_process(retas_compare, emop_job, postproc=True)
        if not retas_compare_proc_pp:
            return
        retas_compare_proc = self.do_process(retas_compare, emop_job, postproc=False)
        if not retas_compare_proc:
            return

        # Append successful completion of page #
        self.append_result(job=emop_job, results=None, failed=False)

    def run(self):
        data = self.payload.load_input()

        if not data:
            logger.error("No payload data to load.")
            return None
        if self.payload.output_exists():
            logger.error("Output file already exists.")
            return None

        for job in data:
            batch_job = EmopBatchJob()
            batch_job.setattrs(job["batch_job"])

            if batch_job.job_type == "ocr":
                self.do_ocr(batch_job=batch_job, job=job)
            # TODO
            # elif batch_job.job_type == "ground truth compare":
            else:
                # TODO print some useful error
                return None

        self.results["job_queues"] = {
            "completed": self.jobs_completed,
            "failed": self.jobs_failed,
        }
        self.results["page_results"] = self.page_results
        self.results["postproc_results"] = self.postproc_results

        # TODO Remove
        print("Payload:")
        print(json.dumps(self.results, sort_keys=True, indent=4))

        # TODO Re-enable
        # self.payload.save_output(self.results)
