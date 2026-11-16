"""Automated tests for the TravelMate expert system. Run: python -m unittest discover -s tests -v"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from knowledge_base import RULES, DESTINATIONS
from inference_engine import build_facts, forward_chain, recommend


def names(result):
    return [r["destination"]["name"] for r in result["recommendations"]]

def fired_ids(result):
    return {r["id"] for r in result["fired_rules"]}

def rule_id(name):
    return next(r["id"] for r in RULES if r["name"] == name)


class KnowledgeBaseTests(unittest.TestCase):
    def test_sizes(self):
        self.assertGreaterEqual(len(RULES), 15)
        self.assertGreaterEqual(len(DESTINATIONS), 20)

    def test_unique_rule_ids(self):
        ids = [r["id"] for r in RULES]
        self.assertEqual(len(ids), len(set(ids)))


class ForwardChainingTests(unittest.TestCase):
    def test_chaining_derives_new_facts(self):
        facts = build_facts({"interests": ["beaches"], "climate": "warm"})
        memory, fired = forward_chain(facts)
        self.assertIn("theme:beach_holiday", memory)       # layer-1 rule
        self.assertIn("match:type:beach", memory)          # layer-2 rule used the derived fact
        order = [r["name"] for r in fired]   # firing order
        self.assertLess(order.index("Beach holiday"), order.index("Beach holiday -> beach destinations"))

    def test_three_level_chain(self):
        facts = build_facts({"companion": "couple", "interests": ["relaxation"], "climate": "cold"})
        memory, _ = forward_chain(facts)
        self.assertIn("theme:honeymoon_hills", memory)

    def test_terminates_and_no_duplicate_firing(self):
        _, fired = forward_chain(build_facts({"interests": list(["adventure", "beaches", "nature"]),
                                              "climate": "warm", "companion": "friends"}))
        ids = [r["id"] for r in fired]
        self.assertEqual(len(ids), len(set(ids)))

    def test_rule_not_fired_without_conditions(self):
        r = recommend({"interests": ["nightlife"], "climate": "warm"})
        self.assertNotIn(rule_id("Beach holiday"), fired_ids(r))


class ScenarioTests(unittest.TestCase):
    def test_low_budget_mountain(self):
        r = recommend({"budget": "low", "climate": "cold", "duration": "medium",
                       "interests": ["mountains"], "companion": "friends", "dest_type": "hill_station"})
        self.assertIn(rule_id("Budget mountain trip"), fired_ids(r))
        for rec in r["recommendations"]:
            self.assertIn("hill_station", rec["destination"]["types"])
            self.assertLessEqual(rec["destination"]["budget"][0], 10000)

    def test_beach_lover(self):
        r = recommend({"budget": "medium", "climate": "warm", "duration": "medium",
                       "interests": ["beaches"], "companion": "friends", "dest_type": "beach"})
        self.assertIn(rule_id("Beach holiday"), fired_ids(r))
        self.assertEqual(names(r)[:2], ["Goa", "Gokarna"])
        for rec in r["recommendations"]:
            self.assertIn("beach", rec["destination"]["types"])

    def test_historical_enthusiast(self):
        r = recommend({"budget": "medium", "climate": "warm", "duration": "short",
                       "interests": ["history", "culture"], "companion": "family", "dest_type": "historical"})
        self.assertIn(rule_id("Heritage trip"), fired_ids(r))
        for rec in r["recommendations"]:
            self.assertIn("historical", rec["destination"]["types"])

    def test_family_nature(self):
        r = recommend({"budget": "medium", "climate": "moderate", "duration": "medium",
                       "interests": ["nature"], "companion": "family", "dest_type": "nature"})
        self.assertIn(rule_id("Family nature trip"), fired_ids(r))
        for rec in r["recommendations"]:
            self.assertIn("family", rec["destination"]["companions"])

    def test_short_weekend_from_delhi(self):
        r = recommend({"budget": "low", "duration": "short", "interests": ["nature"],
                       "companion": "friends", "start_city": "Delhi"})
        self.assertIn(rule_id("Short trip from north India"), fired_ids(r))
        for rec in r["recommendations"]:
            self.assertIn("north", rec["destination"]["short_from"])

    def test_short_trip_rule_needs_city(self):
        r = recommend({"duration": "short", "interests": ["nature"]})
        self.assertNotIn(rule_id("Short trip from north India"), fired_ids(r))

    def test_no_strong_preferences(self):
        r = recommend({"budget": "medium", "climate": "any", "dest_type": "any", "interests": []})
        self.assertEqual(len(r["recommendations"]), 3)
        self.assertGreaterEqual(r["recommendations"][0]["score_pct"], 1)

    def test_totally_empty_preferences(self):
        r = recommend({})
        self.assertEqual(len(r["recommendations"]), 3)

    def test_no_exact_match(self):
        r = recommend({"budget": "very_low", "climate": "cold", "duration": "short",
                       "interests": ["beaches"], "companion": "solo", "dest_type": "beach"})
        self.assertEqual(len(r["recommendations"]), 3)
        self.assertTrue(all(rec["score_pct"] < 100 for rec in r["recommendations"]))
        self.assertTrue(any("closest partial" in n for n in r["notes"]))
        self.assertTrue(all(rec["missed"] for rec in r["recommendations"]))


class RobustnessTests(unittest.TestCase):
    def test_invalid_values_ignored(self):
        r = recommend({"budget": "banana", "interests": ["flying", "nature"], "start_city": None, "climate": 5})
        self.assertEqual(r["preferences"]["interests"], ["nature"])
        self.assertEqual(len(r["recommendations"]), 3)

    def test_none_input(self):
        self.assertEqual(len(recommend(None)["recommendations"]), 3)

    def test_unknown_city_note(self):
        r = recommend({"duration": "short", "start_city": "Atlantis"})
        self.assertTrue(any("Atlantis" in n for n in r["notes"]))

    def test_explanations_reference_fired_rules(self):
        r = recommend({"budget": "low", "climate": "cold", "interests": ["mountains"]})
        fired = fired_ids(r)
        for rec in r["recommendations"]:
            for m in rec["matched"]:
                self.assertTrue(m["rules"] and set(m["rules"]) <= fired)

    def test_scores_in_range_and_sorted(self):
        r = recommend({"budget": "medium", "climate": "warm", "interests": ["beaches", "nightlife"]})
        scores = [x["score_pct"] for x in r["recommendations"] + r["alternatives"]]
        self.assertTrue(all(0 <= s <= 100 for s in scores))
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
