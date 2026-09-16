import tempfile
import unittest
from pathlib import Path

from profile_directory import discover, parse_profile, write_reports


class ProfileTests(unittest.TestCase):
    def test_phases_are_not_double_counted_with_events(self):
        phases, events = parse_profile(
            "import took 1.75s\nfoo took 120ms\ncumulative profiling times:\n"
            "\timport 1.75s\n\ttype checking 21ms\n\ttiny phase 2.5e-3ms\n"
            "\tmicro phase 3µs\n")
        self.assertEqual(phases["import"], 1.75)
        self.assertAlmostEqual(phases["type checking"], 0.021)
        self.assertAlmostEqual(phases["tiny phase"], 0.0000025)
        self.assertAlmostEqual(phases["micro phase"], 0.000003)
        self.assertEqual(events, [{"event": "import", "seconds": 1.75},
                                  {"event": "foo", "seconds": 0.12}])
        self.assertNotIn("elaboration", phases)

    def test_discovery_excludes_dependency_caches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for file in ("A.lean", "Sub/B.lean", ".lake/packages/C.lean", ".git/D.lean"):
                path = root / file
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            self.assertEqual(discover(root), [root / "A.lean", root / "Sub/B.lean"])
            self.assertEqual(discover(root, False), [root / "A.lean"])

    def test_failed_file_and_missing_phases_stay_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            report = write_reports(Path(directory), [
                {"file": "Bad.lean", "wall_seconds": 1.0, "exit_code": 1,
                 "timed_out": False, "log": "logs/Bad.log", "phases": {}, "events": []}])
            self.assertIn("| Bad.lean | 1.000 | — | — | — | — | exit 1 |", report)
            self.assertIn("Bad.lean", (Path(directory) / "summary.csv").read_text())


if __name__ == "__main__":
    unittest.main()
