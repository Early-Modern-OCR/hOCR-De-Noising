import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_settings
from emop.lib.emop_payload import EmopPayload


class TestEmopPayload(TestCase):
    @pytest.fixture(autouse=True)
    def setup_settings(self, tmpdir):
        self.settings = default_settings()
        self.input_path = tmpdir.mkdir("input")
        self.output_path = tmpdir.mkdir("output")
        self.completed_path = self.output_path.mkdir("completed")
        self.uploaded_path = self.output_path.mkdir("uploaded")
        self.settings.payload_input_path = str(self.input_path)
        self.settings.payload_output_path = str(self.output_path)
        self.settings.payload_completed_path = str(self.completed_path)
        self.settings.payload_uploaded_path = str(self.uploaded_path)
        self.payload = EmopPayload(settings=self.settings, proc_id='1')

    def test_input_exists_false(self):
        self.assertEqual(self.payload.input_exists(), False)

    def test_input_exists_true(self):
        self.input_path.join("1.json").write("text")
        self.assertEqual(self.payload.input_exists(), True)

    def test_output_exists_false(self):
        self.assertEqual(self.payload.output_exists(), False)

    def test_output_exists_true(self):
        self.output_path.join("1.json").write("text")
        self.assertEqual(self.payload.output_exists(), True)

    def test_completed_output_exists_false(self):
        self.assertEqual(self.payload.completed_output_exists(), False)

    def test_completed_output_exists_true(self):
        self.completed_path.join("1.json").write("text")
        self.assertEqual(self.payload.completed_output_exists(), True)


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopPayload)
