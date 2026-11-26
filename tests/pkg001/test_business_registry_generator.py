import gzip
import json
import unittest
from pathlib import Path

from runtime.business_registry_generator import build_business_registry
from runtime.property_tenure_generator import _expand_columnar
from runtime.naming import normalize_name
from runtime.naming_inventory import inventory_geography_names

ROOT = Path(__file__).resolve().parents[2]


class BusinessRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = json.loads((ROOT / "data/geography/saltwater-geography-v1.json").read_text())
        with gzip.open(ROOT / "data/property/saltwater-property-world-v1.json.gz", "rt", encoding="utf-8") as source_file:
            world_document = json.load(source_file)
        cls.property_world = _expand_columnar(world_document)
        cls.registry = build_business_registry(source, property_world=cls.property_world)

    def test_registry_meets_ten_thousand_distinct_business_invariant(self):
        rows = self.registry["businesses"]
        ids = [x["business_id"] for x in rows]
        names = [x["registered_name"] for x in rows]
        trading_names = [x["trading_name"] for x in rows]
        self.assertEqual(len(rows), 10000)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(trading_names), len({normalize_name(x) for x in trading_names}))
        self.assertEqual(self.registry["summary"]["distinct_business_count"], 10000)

    def test_business_names_have_no_numeric_placeholder_suffixes(self):
        for row in self.registry["businesses"]:
            self.assertFalse(any(ch.isdigit() for ch in row["trading_name"]), row["trading_name"])
            self.assertFalse(any(ch.isdigit() for ch in row["registered_name"]), row["registered_name"])

    def test_business_names_do_not_collide_with_adopted_geography_names(self):
        geography = inventory_geography_names(json.loads(
            (ROOT / "data/geography/saltwater-geography-v1.json").read_text(encoding="utf-8")
        ))
        reserved = {normalize_name(item.display_name) for item in geography.candidates}
        generated = {
            normalize_name(row["trading_name"]) for row in self.registry["businesses"]
        } | {
            normalize_name(row["registered_name"]) for row in self.registry["businesses"]
        }
        self.assertFalse(generated & reserved)

    def test_every_business_has_one_establishment_and_unit_link(self):
        r = self.registry
        businesses = {x["business_id"] for x in r["businesses"]}
        establishments = {x["establishment_id"]: x for x in r["establishments"]}
        links = {x["business_id"]: x for x in r["business_unit_links"]}
        self.assertEqual(len(establishments), 10000)
        self.assertEqual(len(links), 10000)
        for b in r["businesses"]:
            self.assertIn(b["primary_establishment_id"], establishments)
            self.assertIn(b["business_id"], links)
            self.assertEqual(establishments[b["primary_establishment_id"]]["business_id"], b["business_id"])

    def test_establishments_resolve_full_property_hierarchy(self):
        property_world = self.property_world
        props = {x["property_id"] for x in property_world["properties"]}
        buildings = {x["building_id"] for x in property_world["buildings"]}
        premises = {x["premises_id"] for x in property_world["premises"]}
        units = {x["unit_id"] for x in property_world["units"]}
        addresses = {x["address_id"] for x in property_world["addresses"]}
        for e in self.registry["establishments"]:
            self.assertIn(e["property_id"], props)
            self.assertIn(e["building_id"], buildings)
            self.assertIn(e["premises_id"], premises)
            self.assertIn(e["unit_id"], units)
            self.assertIn(e["address_id"], addresses)

    def test_sector_allocation_is_complete_and_balanced(self):
        expected = {sector: count for sector, count, _ in __import__("runtime.business_registry_generator", fromlist=["SECTORS"]).SECTORS}
        self.assertEqual(self.registry["summary"]["businesses_by_sector"], expected)
        self.assertEqual(sum(expected.values()), 10000)

    def test_no_people_or_population_are_created(self):
        summary = self.registry["summary"]
        self.assertEqual(summary["population_records_created"], 0)
        self.assertEqual(summary["staff_person_records_created"], 0)
        self.assertEqual(self.registry["city_population_hard_cap"], 10000)
        self.assertTrue(all(x["person_records_created"] == 0 for x in self.registry["businesses"]))

    def test_persisted_business_registry_is_valid_columnar_json(self):
        path = ROOT / "data/business/saltwater-business-registry-v1.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(document["schema"], "saltwater-canonical-property-world-columnar/1.0")
        self.assertEqual(document["metadata"]["summary"]["distinct_business_count"], 10000)
        self.assertEqual(len(document["tables"]["businesses"]["rows"]), 10000)
        self.assertEqual(len(document["tables"]["establishments"]["rows"]), 10000)
        business_columns = document["tables"]["businesses"]["columns"]
        trading_name_index = business_columns.index("trading_name")
        persisted_names = [row[trading_name_index] for row in document["tables"]["businesses"]["rows"]]
        generated_names = [row["trading_name"] for row in self.registry["businesses"]]
        self.assertEqual(persisted_names, generated_names)
        self.assertEqual(document["metadata"]["naming"]["standard"], "SW-UNS-001")
        self.assertEqual(
            document["metadata"]["naming"]["near_duplicate_screen"],
            "PASS_WITHIN_ALL_GENERATED_PUBLIC_NAMES",
        )
        self.assertEqual(
            document["metadata"]["naming"]["similarity_algorithm"],
            "POSTGRES_PG_TRGM_COMPATIBLE",
        )
        self.assertEqual(document["metadata"]["naming"]["public_name_count"], 20000)
        self.assertEqual(document["metadata"]["naming"]["reservation_status"],
                         "DRY_RUN_CANDIDATES_NOT_YET_PERSISTENTLY_RESERVED")
        compressed_path = path.with_suffix(path.suffix + ".gz")
        with gzip.open(compressed_path, "rb") as compressed:
            self.assertEqual(compressed.read(), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
