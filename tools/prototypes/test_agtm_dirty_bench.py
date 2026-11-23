#!/usr/bin/env python3
"""Standalone host-only benchmark equivalence and boundary tests."""
import unittest

from agtm_dirty_bench import benchmark, prepare_case, DEFAULT_CASES


class DirtyBenchTests(unittest.TestCase):
    def test_all_prepared_cases_match_oracle(self):
        for case in DEFAULT_CASES:
            with self.subTest(case=case):
                full, dirty, stats, checksum = prepare_case(*case)
                self.assertEqual(full(), dirty()[0])
                self.assertEqual(len(checksum), 64)
                if case[0] == 129:
                    self.assertTrue(stats.full_redraw)
                    self.assertTrue(stats.history_lost)

    def test_minimal_benchmark_records_raw_passes(self):
        result = benchmark(1, 2, cases=((0, 1, 0, 2),))
        self.assertEqual(result["kind"], "HOST_PYTHON_ONLY")
        self.assertEqual(len(result["results"]), 1)
        case = result["results"][0]
        self.assertEqual(case["band_pixels"], 256)
        for values in case["passes_ms"].values():
            self.assertEqual(len(values), 2)


if __name__ == "__main__":
    unittest.main()
