import unittest

import tests.test_emop_settings as test_emop_settings
import tests.test_emop_slurm as test_emop_slurm

tests = [
    test_emop_settings,
    test_emop_slurm,
]

SUITE = unittest.TestSuite([x.suite() for x in tests])

res = unittest.TextTestRunner(verbosity=2).run(SUITE)
