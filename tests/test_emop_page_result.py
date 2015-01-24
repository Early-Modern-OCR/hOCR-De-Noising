from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.models.emop_page_result import EmopPageResult


class TestEmopPageResult(TestCase):
    def setUp(self):
        self.page_result = EmopPageResult(default_settings())

    def test_init(self):
        self.assertIsNone(self.page_result.page_id)
        self.assertIsNone(self.page_result.batch_id)
        self.assertIsNone(self.page_result.ocr_text_path)
        self.assertIsNone(self.page_result.ocr_xml_path)
        self.assertIsNone(self.page_result.corr_ocr_text_path)
        self.assertIsNone(self.page_result.corr_ocr_xml_path)
        self.assertIsNone(self.page_result.juxta_change_index)
        self.assertIsNone(self.page_result.alt_change_index)
        self.assertFalse(self.page_result.page_id_exists)
        self.assertFalse(self.page_result.batch_id_exists)
        self.assertFalse(self.page_result.ocr_text_path_exists)
        self.assertFalse(self.page_result.ocr_xml_path_exists)
        self.assertFalse(self.page_result.corr_ocr_text_path_exists)
        self.assertFalse(self.page_result.corr_ocr_xml_path_exists)
        self.assertFalse(self.page_result.juxta_change_index_exists)
        self.assertFalse(self.page_result.alt_change_index_exists)

    def test_set_existing_attrs_none(self):
        self.page_result.set_existing_attrs(None)
        self.assertFalse(self.page_result.page_id_exists)
        self.assertFalse(self.page_result.batch_id_exists)
        self.assertFalse(self.page_result.ocr_text_path_exists)
        self.assertFalse(self.page_result.ocr_xml_path_exists)
        self.assertFalse(self.page_result.corr_ocr_text_path_exists)
        self.assertFalse(self.page_result.corr_ocr_xml_path_exists)
        self.assertFalse(self.page_result.juxta_change_index_exists)
        self.assertFalse(self.page_result.alt_change_index_exists)

    def test_set_existing_attrs_juxta_change_index(self):
        dictionary = {
            "juxta_change_index": 0.001,
        }
        self.page_result.set_existing_attrs(dictionary)
        self.assertTrue(self.page_result.juxta_change_index_exists)

    def test_to_dict(self):
        self.page_result.page_id = 1
        self.page_result.batch_id = 2
        self.page_result.juxta_change_index = 0.01

        expected_dict = {
            "page_id": 1,
            "batch_id": 2,
            "juxta_change_index": 0.01
        }
        actual_dict = self.page_result.to_dict()

        self.assertItemsEqual(expected_dict, actual_dict)

    def test_has_data_true(self):
        self.page_result.page_id = 1
        self.page_result.batch_id = 2
        self.page_result.juxta_change_index = 0.01

        self.assertTrue(self.page_result.has_data())

    def test_has_data_false(self):
        self.page_result.page_id = 1
        self.page_result.batch_id = 2

        self.assertFalse(self.page_result.has_data())

    def test_ocr_text_path(self):
        self.page_result.settings.output_path_prefix = "/foo"
        self.page_result.ocr_text_path = "/foo/path"

        self.assertEqual("/path", self.page_result.ocr_text_path)

    def test_ocr_xml_path(self):
        self.page_result.settings.output_path_prefix = "/foo"
        self.page_result.ocr_xml_path = "/foo/path"

        self.assertEqual("/path", self.page_result.ocr_xml_path)

    def test_corr_ocr_text_path(self):
        self.page_result.settings.output_path_prefix = "/foo"
        self.page_result.corr_ocr_text_path = "/foo/path"

        self.assertEqual("/path", self.page_result.corr_ocr_text_path)

    def test_corr_ocr_xml_path(self):
        self.page_result.settings.output_path_prefix = "/foo"
        self.page_result.corr_ocr_xml_path = "/foo/path"

        self.assertEqual("/path", self.page_result.corr_ocr_xml_path)


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopPageResult)
