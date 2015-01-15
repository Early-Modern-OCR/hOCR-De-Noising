import unittest

import tests.emop.lib.emop_settings as emop_settings
import tests.emop.lib.schedulers.emop_slurm as emop_slurm

tests = [
    emop_settings,
    emop_slurm,
]

SUITE = unittest.TestSuite([x.suite() for x in tests])

res = unittest.TextTestRunner(verbosity=2).run(SUITE)
