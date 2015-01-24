from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.models.emop_postproc_result import EmopPostprocResult


class TestEmopPostprocResult(TestCase):
    def setUp(self):
        self.postproc_result = EmopPostprocResult(default_settings())

    def test_init(self):
        self.assertIsNone(self.postproc_result.page_id)
        self.assertIsNone(self.postproc_result.batch_job_id)
        self.assertIsNone(self.postproc_result.pp_noisemsr)
        self.assertIsNone(self.postproc_result.pp_ecorr)
        self.assertIsNone(self.postproc_result.pp_juxta)
        self.assertIsNone(self.postproc_result.pp_retas)
        self.assertIsNone(self.postproc_result.pp_health)
        self.assertIsNone(self.postproc_result.pp_pg_quality)
        self.assertIsNone(self.postproc_result.noisiness_idx)
        self.assertIsNone(self.postproc_result.multicol)
        self.assertIsNone(self.postproc_result.skew_idx)
        self.assertFalse(self.postproc_result.page_id_exists)
        self.assertFalse(self.postproc_result.batch_job_id_exists)
        self.assertFalse(self.postproc_result.pp_noisemsr_exists)
        self.assertFalse(self.postproc_result.pp_ecorr_exists)
        self.assertFalse(self.postproc_result.pp_juxta_exists)
        self.assertFalse(self.postproc_result.pp_retas_exists)
        self.assertFalse(self.postproc_result.pp_health_exists)
        self.assertFalse(self.postproc_result.pp_pg_quality_exists)
        self.assertFalse(self.postproc_result.noisiness_idx_exists)
        self.assertFalse(self.postproc_result.multicol_exists)
        self.assertFalse(self.postproc_result.skew_idx_exists)

    def test_set_existing_attrs_none(self):
        self.postproc_result.set_existing_attrs(None)
        self.assertFalse(self.postproc_result.page_id_exists)
        self.assertFalse(self.postproc_result.batch_job_id_exists)
        self.assertFalse(self.postproc_result.pp_noisemsr_exists)
        self.assertFalse(self.postproc_result.pp_ecorr_exists)
        self.assertFalse(self.postproc_result.pp_juxta_exists)
        self.assertFalse(self.postproc_result.pp_retas_exists)
        self.assertFalse(self.postproc_result.pp_health_exists)
        self.assertFalse(self.postproc_result.pp_pg_quality_exists)
        self.assertFalse(self.postproc_result.noisiness_idx_exists)
        self.assertFalse(self.postproc_result.multicol_exists)
        self.assertFalse(self.postproc_result.skew_idx_exists)

    def test_set_existing_attrs_pp_pg_quality(self):
        dictionary = {
            "pp_pg_quality": 0.01,
        }
        self.postproc_result.set_existing_attrs(dictionary)
        self.assertTrue(self.postproc_result.pp_pg_quality_exists)

    def test_to_dict(self):
        self.postproc_result.page_id = 1
        self.postproc_result.batch_job_id = 2
        self.postproc_result.pp_pg_quality = 0.01
        self.postproc_result.pp_ecorr = None

        expected_dict = {
            "page_id": 1,
            "batch_job_id": 2,
            "pp_pg_quality": 0.01
        }
        actual_dict = self.postproc_result.to_dict()

        self.assertItemsEqual(expected_dict, actual_dict)

    def test_has_data_true(self):
        self.postproc_result.page_id = 1
        self.postproc_result.batch_job_id = 2
        self.postproc_result.pp_pg_quality = 0.01

        self.assertTrue(self.postproc_result.has_data())

    def test_has_data_false(self):
        self.postproc_result.page_id = 1
        self.postproc_result.batch_job_id = 2

        self.assertFalse(self.postproc_result.has_data())


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopPostprocResult)
