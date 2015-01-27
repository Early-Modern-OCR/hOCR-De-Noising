from flexmock import flexmock
import os
import signal
import subprocess32
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
import emop.lib.utilities
from emop.lib.utilities import *


class TestUtilities(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess32.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv
        self.signal_patcher = mock.patch("emop.lib.utilities.signal.signal")
        #self.mock_signal = self.signal_patcher.start()

    def tearDown(self):
        self.popen_patcher.stop()
        #self.signal_patcher.stop()

    def test_get_temp_dir_none(self):
        if os.environ.get("TMPDIR"):
            del os.environ["TMPDIR"]
        self.assertEqual(get_temp_dir(), None)

    def test_get_temp_dir_exists(self):
        os.environ["TMPDIR"] = "/dne"
        self.assertEqual(get_temp_dir(), "/dne")

    def test_exec_cmd_string_cmd(self):
        exec_cmd(cmd="sleep 1")
        actual_args, actual_kwargs = self.mock_popen.call_args

        self.assertEqual(["sleep", "1"], actual_args[0])

    def test_exec_cmd_2d_list(self):
        exec_cmd(cmd=["ls", ["-l", "-a"], "./"])
        actual_args, actual_kwargs = self.mock_popen.call_args

        self.assertEqual(["ls", "-l", "-a", "./"], actual_args[0])

    def test_exec_cmd_return(self):
        expected_proc = mock_proc_tuple("Foo", "Bar", 1)
        self.mock_rv.returncode = 1
        self.mock_rv.communicate.return_value[0] = "Foo"
        self.mock_rv.communicate.return_value[1] = "Bar"
        retval = exec_cmd(cmd="test 0")

        self.assertEqual(expected_proc, retval)

    def test_exec_cmd_catch_OSError(self):
        expected_msg = "File not found for command: [Errno 2] foo"
        expected_proc = mock_proc_tuple(expected_msg, expected_msg, 1)
        self.mock_popen.side_effect = OSError(os.errno.ENOENT, 'foo')
        retval = exec_cmd(cmd="foo")

        self.assertEqual(expected_proc, retval)

    def test_exec_cmd_timeout(self):
        self.popen_patcher.stop()
        expected_proc = mock_proc_tuple("Command timed out", "Command timed out", 1)
        retval = exec_cmd(cmd="sleep 2", timeout=1)
        self.popen_patcher.start()

        self.assertRaises(subprocess32.TimeoutExpired)
        self.assertEqual(expected_proc, retval)

    def test_exec_cmd_timeout_disabled(self):
        self.popen_patcher.stop()
        expected_proc = mock_proc_tuple("", "", 0)
        retval = exec_cmd(cmd="sleep 2")
        self.popen_patcher.start()

        self.assertEqual(expected_proc, retval)


def suite():
    return TestLoader().loadTestsFromTestCase(TestUtilities)
