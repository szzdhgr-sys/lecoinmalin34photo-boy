import unittest
from bot_v7_search import (
    BRANDS, brands_for_ids, extract_brands, ids_for_brand,
    index_entry, index_export_messages, matched, normalized, search_ids,
)


class SearchV7Tests(unittest.TestCase):
    def test_normalization_accents(self):
        self.assertEqual(normalized("Hermès !"), "hermes")
        self.assertTrue(matched("AirPods Pro 2 - Apple", "airpods pro 2"))

    def test_search_word_order(self):
        self.assertTrue(matched("Nike Air Max TN", "tn nike"))
        self.assertFalse(matched("Nike Air Max TN", "Dior B30"))

    def test_detect_only_explicit_brands(self):
        self.assertIn("Prada", extract_brands("Chaussures Prada Cup"))
        self.assertIn("Louis Vuitton", extract_brands("Sacoche Louis Vuitton"))
        self.assertIn("Hermès", extract_brands("Sandales Hermès"))
        self.assertNotIn("Nike", extract_brands("Nikee sans marque"))

    def test_message_index(self):
        entry = index_entry({"caption": "Doudoune Moncler taille M"})
        self.assertEqual(entry["brands"], ["Moncler"])
        self.assertIsNone(index_entry({"photo": ["unused"]}))

    def test_export_messages_indexed(self):
        records = index_export_messages([
            {"type": "message", "id": 5, "text": ["Ensemble ", {"type": "plain", "text": "Essentials"}]},
            {"type": "service", "id": 6, "text": "Gucci"},
            {"type": "message", "id": 7, "text": "AirPods Pro 2"},
        ])
        self.assertSetEqual(set(records), {"5", "7"})
        self.assertEqual(records["7"]["brands"], ["Apple"])

    def test_scope_and_recency(self):
        entries = {
            "3": {"text": "Nike Air Max", "brands": ["Nike"]},
            "9": {"text": "Nike Dunk", "brands": ["Nike"]},
            "10": {"text": "Prada", "brands": ["Prada"]},
        }
        self.assertEqual(search_ids([3, 9, 10, 9], entries, "nike"), [9, 3])
        self.assertEqual(ids_for_brand([10, 3, 9, 3], entries, "Nike"), [9, 3])
        self.assertEqual(brands_for_ids([3, 9, 10], entries),
                         [("Nike", 2), ("Prada", 1)])

    def test_brand_indices(self):
        self.assertLess(len(BRANDS), 100)
        self.assertEqual(len(BRANDS), len(set(BRANDS)))


if __name__ == "__main__":
    unittest.main()
