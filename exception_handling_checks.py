import importlib
import math
from pathlib import Path


def raise_os_error():
    raise OSError("Controlled file-access failure")


def raise_eof_error():
    raise EOFError("Controlled end-of-input")


def test_case(label, expected_type, operation):
    try:
        operation()
    except expected_type as error:
        caught_name = type(error).__name__
        print(f"PASS | {label}: caught {caught_name}")
        return True
    except Exception as error:
        print(f"FAIL | {label}: expected {expected_type.__name__}, caught {type(error).__name__}")
        return False
    print(f"FAIL | {label}: expected {expected_type.__name__}, no exception was raised")
    return False


def run_checks():
    print("BBIM502 - Controlled Exception Handling Checks")
    print("These checks run isolated test cases; application data is not changed.\n")
    checks = [
        ("SyntaxError", SyntaxError, lambda: compile("if True print('bad')", "<probe>", "exec")),
        ("ValueError", ValueError, lambda: int("not-a-number")),
        ("ZeroDivisionError", ZeroDivisionError, lambda: 12 / 0),
        ("IndexError", IndexError, lambda: [][0]),
        ("NameError", NameError, lambda: eval("undefined_probe_name")),
        ("TypeError", TypeError, lambda: 12 + "12"),
        ("OverflowError", OverflowError, lambda: math.exp(10000)),
        ("IOError", IOError, raise_os_error),
        ("ImportError", ImportError, lambda: importlib.import_module("missing_bbim502_probe_module_987654")),
        ("EOFError", EOFError, raise_eof_error),
        ("FileNotFoundError", FileNotFoundError, lambda: Path("missing_bbim502_probe_file.txt").read_text(encoding="utf-8")),
    ]
    outcomes = [test_case(label, expected, operation) for label, expected, operation in checks]
    passed = sum(outcomes)
    failed = len(outcomes) - passed
    print(f"\nResult: {passed}/{len(outcomes)} exception probes passed; {failed} failed.")
    return failed == 0


if __name__ == "__main__":
    raise SystemExit(0 if run_checks() else 1)
