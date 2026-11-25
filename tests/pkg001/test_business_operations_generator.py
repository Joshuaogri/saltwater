import json
import unittest
from pathlib import Path

from runtime.business_operations_generator import build_business_operations
from runtime.property_tenure_generator import _expand_columnar

ROOT = Path(__file__).resolve().parents[2]


class CanonicalBusinessOperationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8"))
        registry_document = json.loads((ROOT / "data/business/saltwater-business-registry-v1.json").read_text(encoding="utf-8"))
        cls.registry = _expand_columnar(registry_document)
        cls.operations = build_business_operations(source, registry=cls.registry)

    def test_every_business_has_seven_daily_schedules(self):
        o = self.operations
        self.assertEqual(o["summary"]["business_count"], 10000)
        self.assertEqual(o["summary"]["daily_schedule_count"], 70000)
        self.assertEqual(o["summary"]["weekly_profile_count"], 10000)
        self.assertEqual(len({x["business_schedule_id"] for x in o["daily_schedules"]}), 70000)

    def test_schedules_resolve_to_business_establishments(self):
        business_ids = {f"SWBIZ-{i:06d}" for i in range(1, 10001)}
        for row in self.operations["daily_schedules"]:
            self.assertIn(row["business_id"], business_ids)
            self.assertEqual(row["establishment_id"], f"SWEST-{row['business_id'][-6:]}")
            self.assertEqual(row["valid_from_tick"], 0)
            self.assertEqual(row["valid_to_tick"], None)

    def test_open_and_closed_days_have_consistent_times(self):
        for row in self.operations["daily_schedules"]:
            if row["is_open_to_customers"]:
                self.assertRegex(row["customer_open_time"], r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
                self.assertRegex(row["customer_close_time"], r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
                self.assertTrue(row["service_window"])
                self.assertTrue(row["staff_shift_pattern"])
            else:
                self.assertIsNone(row["customer_open_time"])
                self.assertIsNone(row["customer_close_time"])

    def test_inactive_businesses_never_show_as_open(self):
        for row in self.operations["daily_schedules"]:
            if row["operating_status"] == "temporarily_inactive":
                self.assertFalse(row["is_open_to_customers"])
                self.assertEqual(row["service_window"], "temporarily_suspended")

    def test_schedules_do_not_create_people_or_population(self):
        self.assertEqual(self.operations["summary"]["population_records_created"], 0)
        self.assertEqual(self.operations["city_population_hard_cap"], 10000)

    def test_all_days_are_present_for_every_business(self):
        grouped = {}
        for row in self.operations["daily_schedules"]:
            grouped.setdefault(row["business_id"], set()).add(row["day_of_week"])
        self.assertEqual(len(grouped), 10000)
        self.assertTrue(all(len(days) == 7 for days in grouped.values()))


if __name__ == "__main__":
    unittest.main()
