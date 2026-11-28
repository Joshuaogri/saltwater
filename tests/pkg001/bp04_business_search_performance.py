"""Reproducible 10k-business in-memory search latency acceptance."""

from __future__ import annotations

import gzip
import json
import statistics
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.bp04_lookup import BP04Lookup, SEARCH_FIELDS, _normalise


ARCHIVES = {
    "SW-PROPERTY-WORLD-V1": ROOT / "data/property/saltwater-property-world-v1.json.gz",
    "SW-BUSINESS-REGISTRY-V1": ROOT / "data/business/saltwater-business-registry-v1.json.gz",
}


class BP04BusinessSearchPerformanceAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        documents = {
            dataset_id: json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
            for dataset_id, path in ARCHIVES.items()
        }
        started = time.perf_counter_ns()
        with patch(
            "runtime.bp04_lookup.load_dataset",
            side_effect=lambda _conn, dataset_id: documents[dataset_id],
        ):
            cls.lookup = BP04Lookup(None)
        cls.index_build_ms = (time.perf_counter_ns() - started) / 1_000_000
        cls.businesses = cls.lookup._search_rows["business"]

    def test_10k_business_substring_queries_meet_latency_budget(self):
        self.assertEqual(len(self.businesses), 10_000)
        queries = []
        for row in self.businesses[:1000]:
            for field in ("trading_name", "registered_name"):
                value = _normalise(row.get(field))
                if len(value) >= 4:
                    queries.append(value[:4])
                    break
        self.assertEqual(len(queries), 1000)

        # Compare a deterministic sample against the former linear semantics.
        for query in queries[:100]:
            needle = _normalise(query)
            expected = []
            for record in self.businesses:
                haystack = " ".join(
                    _normalise(record.get(field))
                    for field in SEARCH_FIELDS["business"]
                )
                if needle in haystack:
                    expected.append(record["business_id"])
            expected.sort()
            actual = [
                row["business_id"]
                for row in self.lookup.search("business", query, limit=100)
            ]
            self.assertEqual(actual, expected[:100], query)

        # Warm the interpreter/index, then measure 1,000 independent lookups.
        for query in queries[:50]:
            self.lookup.search("business", query, limit=20)
        timings_ms = []
        result_count = 0
        for query in queries:
            started = time.perf_counter_ns()
            results = self.lookup.search("business", query, limit=20)
            timings_ms.append((time.perf_counter_ns() - started) / 1_000_000)
            result_count += len(results)

        ordered = sorted(timings_ms)
        p50 = statistics.median(ordered)
        p95 = ordered[int((len(ordered) - 1) * 0.95)]
        p99 = ordered[int((len(ordered) - 1) * 0.99)]
        report = {
            "dataset": "SW-BUSINESS-REGISTRY-V1",
            "business_count": len(self.businesses),
            "query_count": len(queries),
            "result_rows_returned": result_count,
            "index_build_ms": round(self.index_build_ms, 3),
            "search_p50_ms": round(p50, 4),
            "search_p95_ms": round(p95, 4),
            "search_p99_ms": round(p99, 4),
            "search_max_ms": round(max(ordered), 4),
            "budget": {"p95_ms_max": 10.0, "p99_ms_max": 25.0},
        }
        print("BP04_BUSINESS_SEARCH_BENCHMARK=" + json.dumps(report, sort_keys=True))
        self.assertLessEqual(p95, 10.0, report)
        self.assertLessEqual(p99, 25.0, report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
