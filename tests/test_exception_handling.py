import contextlib
import io
import unittest

from exception_handling_checks import run_checks


class ExceptionProbeTests(unittest.TestCase):
    def test_all_required_exception_probes_pass(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(run_checks())


if __name__ == "__main__":
    unittest.main()
