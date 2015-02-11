import json
import os
from unittest import TestCase

class TestEmopEcco(TestCase):
    def setUp(self):
        test_root = os.path.dirname(__file__)
        fixture_dir = os.path.join(test_root, 'fixtures')
        fixture_file = os.path.join(fixture_dir, 'ecco-small-output.json')
        with open(fixture_file) as datafile:
            self.fixture_data = json.load(datafile)

        self.test_file = os.path.join(test_root, 'payload/output/completed/ecco-small.json')
        with open(self.test_file) as datafile:
            self.test_data = json.load(datafile)

    def get_page_results_values(self, key):
        fixture_page_results = sorted(self.fixture_data["page_results"], key=lambda k: k["page_id"])
        test_page_results = sorted(self.test_data["page_results"], key=lambda k: k["page_id"])

        fixture_values = [d[key] for d in fixture_page_results]
        test_values = [d[key] for d in test_page_results]

        return fixture_values, test_values

    def get_postproc_results_values(self, key):
        fixture_postproc_results = sorted(self.fixture_data["postproc_results"], key=lambda k: k["page_id"])
        test_postproc_results = sorted(self.test_data["postproc_results"], key=lambda k: k["page_id"])

        fixture_values = [d[key] for d in fixture_postproc_results]
        test_values = [d[key] for d in test_postproc_results]

        return fixture_values, test_values

    def test_job_queues_completed(self):
        job_queues_completed = self.test_data["job_queues"]["completed"]

        self.assertEqual(10, len(job_queues_completed))

    def test_job_queues_failed(self):
        job_queues_failed = self.test_data["job_queues"]["failed"]

        self.assertEqual(0, len(job_queues_failed))

    def test_page_result_paths(self):
        fixture_ocr_text_paths, test_ocr_text_paths = self.get_page_results_values("ocr_text_path")
        fixture_ocr_xml_paths, test_ocr_xml_paths = self.get_page_results_values("ocr_xml_path")
        fixture_corr_ocr_text_paths, test_corr_ocr_text_paths = self.get_page_results_values("corr_ocr_text_path")
        fixture_corr_ocr_xml_paths, test_corr_ocr_xml_paths = self.get_page_results_values("corr_ocr_xml_path")

        self.assertEqual(fixture_ocr_text_paths, test_ocr_text_paths)
        self.assertEqual(fixture_ocr_xml_paths, test_ocr_xml_paths)
        self.assertEqual(fixture_corr_ocr_text_paths, test_corr_ocr_text_paths)
        self.assertEqual(fixture_corr_ocr_xml_paths, test_corr_ocr_xml_paths)

    def test_juxta_change_index(self):
        fixture_juxta_change_indexes, test_juxta_change_indexes = self.get_page_results_values("juxta_change_index")

        self.assertEqual(fixture_juxta_change_indexes, test_juxta_change_indexes)

    def test_pp_noisemsr(self):
        fixture_pp_noisemsrs, test_pp_noisemsrs = self.get_postproc_results_values("pp_noisemsr")

        self.assertEqual(fixture_pp_noisemsrs, test_pp_noisemsrs)

    def test_multicol(self):
        fixture_multicols, test_multicols = self.get_postproc_results_values("multicol")

        self.assertEqual(fixture_multicols, test_multicols)

    def test_skew_idx(self):
        fixture_skew_idxs, test_skew_idxs = self.get_postproc_results_values("skew_idx")

        self.assertEqual(fixture_skew_idxs, test_skew_idxs)

    def test_pp_ecorr(self):
        fixture_pp_ecorrs, test_pp_ecorrs = self.get_postproc_results_values("pp_ecorr")

        self.assertEqual(fixture_pp_ecorrs, test_pp_ecorrs)

    def test_pp_pg_quality(self):
        fixture_pp_pg_qualitys, test_pp_pg_qualitys = self.get_postproc_results_values("pp_pg_quality")

        self.assertEqual(fixture_pp_pg_qualitys, test_pp_pg_qualitys)

    def test_pp_health(self):
        fixture_pp_healths, test_pp_healths = self.get_postproc_results_values("pp_health")

        self.assertEqual(fixture_pp_healths, test_pp_healths)
