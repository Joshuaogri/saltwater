import unittest

from runtime.naming import (
    NameCollision, NameRegistry, NameReviewRequired, NamingError, normalize_name,
)


class NamingNormalizationTests(unittest.TestCase):
    def test_unicode_nfkc_and_casefold_are_deterministic(self):
        self.assertEqual(normalize_name("  STRASSE  "), normalize_name("Straße"))
        self.assertEqual(normalize_name("Ｆｏｕｎｄｒｙ　Street"), "foundry street")

    def test_punctuation_spacing_and_road_suffix_variants_match(self):
        self.assertEqual(normalize_name("Bellview Crescent"), normalize_name("  BELLVIEW-CRES "))
        self.assertEqual(normalize_name("Foundry Road"), normalize_name("Foundry Rd"))

    def test_display_spelling_is_not_rewritten(self):
        registry = NameRegistry()
        record = registry.reserve("geography_road", "road-1", "St. John's Road")
        self.assertEqual(record.display_name, "St. John's Road")

    def test_empty_and_control_character_names_are_rejected(self):
        for value in ("  ", "Road\nName"):
            with self.subTest(value=value), self.assertRaises(NamingError):
                normalize_name(value)


class NamingRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = NameRegistry()

    def test_exact_duplicate_is_rejected_across_entity_types(self):
        self.registry.reserve("geography_road", "r1", "Bellview Crescent")
        with self.assertRaises(NameCollision):
            self.registry.reserve("business", "b1", "Bellview Crescent")

    def test_case_and_punctuation_collision_is_rejected(self):
        self.registry.reserve("geography_road", "r1", "Foundry Road")
        with self.assertRaises(NameCollision):
            self.registry.reserve("business", "b1", "FOUNDRY Rd")

    def test_near_duplicate_is_held_for_review(self):
        self.registry.reserve("geography_road", "r1", "Ashbourne Road")
        with self.assertRaises(NameReviewRequired):
            self.registry.reserve("geography_road", "r2", "Ashburn Road")

    def test_retired_name_cannot_be_reassigned(self):
        self.registry.reserve("business", "b1", "Harbour House")
        self.registry.retire("business", "b1", "Harbour House")
        with self.assertRaises(NameCollision):
            self.registry.reserve("business", "b2", "Harbour House")

    def test_alias_collision_is_rejected(self):
        self.registry.reserve("person", "p1", "Amara Nneka Okafor")
        self.registry.reserve("person", "p1", "Nneka", name_form="alias")
        with self.assertRaises(NameCollision):
            self.registry.reserve("business", "b1", "Nneka")

    def test_rename_preserves_old_reservation_and_entity_id(self):
        self.registry.reserve("geography_road", "road-1", "Old Quay Road")
        new = self.registry.rename("geography_road", "road-1", "Harbour View Road")
        self.assertEqual(new.entity_id, "road-1")
        with self.assertRaises(NameCollision):
            self.registry.reserve("business", "b1", "Old Quay Road")
        result = self.registry.search("Old Quay Road")
        self.assertEqual(result.records[0].status, "superseded")

    def test_name_search_reports_ambiguity_for_saltwater_roots(self):
        self.registry.reserve("geography_sovereign_root", "saltwater-state", "Saltwater")
        self.registry.reserve("geography_playable_city", "saltwater-city", "Saltwater")
        result = self.registry.search("Saltwater")
        self.assertTrue(result.ambiguous)
        self.assertEqual(len(result.records), 2)

    def test_only_the_exact_two_root_entities_may_share_saltwater(self):
        self.registry.reserve("geography_sovereign_root", "saltwater-state", "Saltwater")
        self.registry.reserve("geography_playable_city", "saltwater-city", "Saltwater")
        for entity_type, entity_id, name, form in (
            ("person", "p1", "Saltwater", "canonical"),
            ("business", "b1", "Saltwater", "canonical"),
            ("geography_road", "r1", "Saltwater", "canonical"),
            ("geography_sovereign_root", "saltwater-state", "Saltwater", "alias"),
        ):
            with self.subTest(entity_type=entity_type, form=form), self.assertRaises(NameCollision):
                self.registry.reserve(entity_type, entity_id, name, name_form=form)

    def test_name_only_search_never_selects_one_root(self):
        self.registry.reserve("geography_sovereign_root", "saltwater-state", "Saltwater")
        self.registry.reserve("geography_playable_city", "saltwater-city", "Saltwater")
        self.assertEqual(
            {r.entity_id for r in self.registry.search("Saltwater").records},
            {"saltwater-state", "saltwater-city"},
        )


from runtime.name_generation import GeneratorConfig, generate_batch, generate_candidates


class NameGenerationTests(unittest.TestCase):
    def setUp(self):
        self.config = GeneratorConfig(
            given_names=("Amara", "Tariq", "Evelyn", "Kelechi"),
            middle_names=("Nneka", "James", "Ife", "Rose"),
            family_names=("Okafor", "Mensah", "Bennett", "Adeyemi"),
            place_roots=("Willowbank", "Bellview", "Foundry", "Quayside"),
            business_roots=("Harbour", "Meridian", "Foundry", "Civic"),
        )

    def test_generation_is_reproducible_for_same_seed(self):
        a = generate_candidates("person", 12, seed=44, config=self.config)
        b = generate_candidates("person", 12, seed=44, config=self.config)
        self.assertEqual(a, b)
        self.assertEqual(len({normalize_name(x) for x in a}), 12)

    def test_road_generation_varies_road_forms(self):
        values = generate_candidates("road", 20, seed=12, config=self.config)
        self.assertGreaterEqual(len({x.rsplit(" ", 1)[-1] for x in values}), 4)

    def test_business_generation_is_deterministic_and_unique(self):
        values = generate_candidates("business", 12, seed=9, config=self.config)
        self.assertEqual(len(values), len({normalize_name(x) for x in values}))

    def test_batch_records_version_seed_and_reproducible_manifest(self):
        a = generate_batch("person", 8, seed=71, config=self.config)
        b = generate_batch("person", 8, seed=71, config=self.config)
        self.assertEqual(a, b)
        self.assertEqual(a.generator_version, 1)
        self.assertEqual(a.config_version, "1")
        self.assertEqual(len(a.manifest_sha256), 64)

    def test_generator_refuses_exhausted_vocabulary_instead_of_adding_numbers(self):
        tiny = GeneratorConfig(("A",), ("B",), ("C",), ("Only",), ("Only",), ("Works",))
        with self.assertRaises(NamingError):
            generate_candidates("person", 2, seed=1, config=tiny)


if __name__ == "__main__":
    unittest.main()
