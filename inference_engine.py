"""
inference_engine.py  --  forward-chaining INFERENCE ENGINE of TravelMate.

Pipeline
  1. build_facts()      user preferences -> initial facts (working memory)
  2. forward_chain()    FORWARD CHAINING: repeatedly fire rules whose IF part
                        is satisfied by the facts, adding the THEN facts, until
                        no rule can fire any more.
  3. collect_matches()  keep the "match:" facts that the rules derived
  4. rank()             compare derived facts with each destination's facts
                        and compute a rule-based match score
  5. explain            every recommendation lists the rules and reasons.

Note: only step 2 is forward chaining. Steps 3-4 are a scoring step that works
on the facts produced by step 2.
"""
from knowledge_base import (BUDGET_OPTIONS, CLIMATE_OPTIONS, DURATION_OPTIONS,
                            INTEREST_OPTIONS, COMPANION_OPTIONS, TYPE_OPTIONS,
                            CITY_REGIONS, RULES, DESTINATIONS, BUDGET_CAPS,
                            destination_facts)

DEFAULTS = {"budget": "low", "climate": "any", "duration": "medium",
            "interests": [], "companion": "friends", "dest_type": "any",
            "start_city": ""}


def clean_preferences(prefs):
    """Fill in defaults and drop invalid values so incomplete input never crashes."""
    prefs = dict(prefs or {})
    out = dict(DEFAULTS)
    valid = {"budget": set(BUDGET_OPTIONS.values()), "climate": set(CLIMATE_OPTIONS.values()),
             "duration": set(DURATION_OPTIONS.values()), "companion": set(COMPANION_OPTIONS.values()),
             "dest_type": set(TYPE_OPTIONS.values())}
    for key, allowed in valid.items():
        if prefs.get(key) in allowed:
            out[key] = prefs[key]
    interests = prefs.get("interests") or []
    out["interests"] = [i for i in dict.fromkeys(interests) if i in INTEREST_OPTIONS.values()]
    out["start_city"] = str(prefs.get("start_city") or "").strip()
    return out


def build_facts(prefs):
    """Step 1: convert preferences into the initial facts (a set of strings)."""
    p = clean_preferences(prefs)
    facts = {"budget:" + p["budget"], "duration:" + p["duration"],
             "companion:" + p["companion"]}
    if p["climate"] != "any":
        facts.add("climate:" + p["climate"])
    if p["dest_type"] != "any":
        facts.add("type:" + p["dest_type"])
    facts.update("interest:" + i for i in p["interests"])
    region = CITY_REGIONS.get(p["start_city"].lower())
    if region:
        facts.add("origin:" + region)
    return facts


def _condition_met(condition, memory):
    """A condition is met if any of its '|' alternatives is in working memory."""
    return any(option in memory for option in condition.split("|"))


def forward_chain(initial_facts, rules=RULES):
    """
    Step 2: FORWARD CHAINING.
    Loop: look at every rule not yet fired; if all its conditions are in
    working memory, fire it (add its THEN facts). Each rule fires at most once
    and facts are stored in a set, so there are no duplicates and no infinite
    loops. Stop when a full pass fires nothing new.
    """
    memory = set(initial_facts)
    fired, fired_ids, cycle, changed = [], set(), 0, True
    while changed:
        changed = False
        cycle += 1
        for rule in rules:
            if rule["id"] in fired_ids:
                continue
            if all(_condition_met(c, memory) for c in rule["if"]):
                new_facts = sorted(f for f in rule["then"] if f not in memory)
                memory.update(rule["then"])
                fired_ids.add(rule["id"])
                fired.append({"id": rule["id"], "name": rule["name"], "cycle": cycle,
                              "if": rule["if"], "then": rule["then"],
                              "because": rule["because"], "weight": rule["weight"],
                              "new_facts": new_facts})
                changed = True
    return memory, fired


def collect_matches(fired):
    """Step 3: gather 'match:' conclusions -> {attribute fact: {weight, rules}}."""
    matches = {}
    for r in fired:
        for fact in r["then"]:
            if fact.startswith("match:"):
                target = fact[len("match:"):]
                entry = matches.setdefault(target, {"weight": 0, "rules": [], "reasons": []})
                entry["weight"] = max(entry["weight"], r["weight"])
                entry["rules"].append(r["id"])
                entry["reasons"].append(r["because"])
    return matches


def describe_fact(fact):
    """Turn 'interest:beaches' into friendly text."""
    key, _, value = fact.partition(":")
    nice = value.replace("_", " ")
    if key == "affordable":
        labels = {v: k for k, v in BUDGET_OPTIONS.items()}
        return "Approximate cost fits your budget (%s)" % labels.get(value, nice)
    if key == "short_trip_from":
        return "Good short trip from %s India" % nice
    if key == "feature":
        return "Has feature: %s destination" % nice
    names = {"interest": "Interest", "type": "Destination type", "climate": "Climate",
             "duration": "Trip length", "companion": "Suitable for"}
    return "%s: %s" % (names.get(key, key.title()), nice)


def rank(matches, prefs):
    """Step 4: score every destination against the derived match facts."""
    total = sum(m["weight"] for m in matches.values())
    results = []
    for dest in DESTINATIONS:
        facts = destination_facts(dest)
        matched = [t for t in matches if t in facts]
        missed = [t for t in matches if t not in facts]
        got = sum(matches[t]["weight"] for t in matched)
        pct = round(100.0 * got / total) if total else None
        results.append({
            "destination": dest, "score_pct": pct, "score_points": got,
            "max_points": total,
            "matched": [{"fact": t, "text": describe_fact(t), "rules": matches[t]["rules"],
                         "reason": matches[t]["reasons"][0]} for t in matched],
            "missed": [{"fact": t, "text": describe_fact(t)} for t in missed],
        })
    key = lambda r: (-(r["score_pct"] or 0), -r["destination"]["popularity"], r["destination"]["name"])
    return sorted(results, key=key)


def recommend(prefs, top_n=3, alt_n=3):
    """Run the full expert system and return everything the UI needs."""
    p = clean_preferences(prefs)
    initial = build_facts(p)
    memory, fired = forward_chain(initial)
    matches = collect_matches(fired)
    ranked = rank(matches, p)
    no_prefs = (not p["interests"]) and p["climate"] == "any" and p["dest_type"] == "any"
    best = ranked[0]["score_pct"] if (ranked and matches) else None
    notes = []
    if no_prefs:
        notes.append("You gave no interests, climate or destination type, so only budget, duration and companions were used. Popular destinations win ties.")
    if best is not None and best < 100:
        notes.append("No destination satisfies every preference. The closest partial matches are shown; "
                     "see each explanation for what was missed.")
    if p["start_city"] and "origin:" not in " ".join(initial):
        notes.append("Starting city '%s' is not in the knowledge base, so distance rules were skipped." % p["start_city"])
    return {"preferences": p, "initial_facts": sorted(initial),
            "derived_facts": sorted(memory - initial), "fired_rules": fired,
            "recommendations": ranked[:top_n], "alternatives": ranked[top_n:top_n + alt_n],
            "no_preferences": no_prefs, "notes": notes}
