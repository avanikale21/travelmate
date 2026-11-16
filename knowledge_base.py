"""
knowledge_base.py  --  the KNOWLEDGE BASE of TravelMate.

Contains:
  1. Vocabulary (budget levels, climates, interests ...) used by form + rules
  2. DESTINATIONS  - facts about each place
  3. RULES         - IF-THEN production rules used by the inference engine
  4. browse()      - plain search/filter used ONLY by the Destination Explorer
                     (this is ordinary filtering, NOT forward chaining)

Facts are simple strings of the form "attribute:value", e.g. "interest:beaches".
"""

# ----------------------------------------------------------------------------
# 1. Vocabulary  (form label -> internal key)
# ----------------------------------------------------------------------------
BUDGET_OPTIONS = {
    "Below ₹5,000": "very_low",
    "₹5,000–₹10,000": "low",
    "₹10,000–₹20,000": "medium",
    "₹20,000–₹40,000": "high",
    "Above ₹40,000": "luxury",
}
BUDGET_CAPS = {"very_low": 5000, "low": 10000, "medium": 20000, "high": 40000,
               "luxury": float("inf")}
CLIMATE_OPTIONS = {"Cold": "cold", "Moderate": "moderate", "Warm": "warm",
                   "No preference": "any"}
DURATION_OPTIONS = {"1–2 days": "short", "3–5 days": "medium",
                    "6–8 days": "long", "More than 8 days": "extended"}
INTEREST_OPTIONS = {"Adventure": "adventure", "Beaches": "beaches",
                    "Mountains": "mountains", "Nature": "nature",
                    "Historical places": "history", "Culture": "culture",
                    "Wildlife": "wildlife", "Relaxation": "relaxation",
                    "Nightlife": "nightlife"}
COMPANION_OPTIONS = {"Solo": "solo", "Friends": "friends", "Family": "family",
                     "Couple": "couple"}
TYPE_OPTIONS = {"Any": "any", "Hill station": "hill_station", "Beach": "beach",
                "City": "city", "Historical destination": "historical",
                "Nature destination": "nature"}

# Where the traveller starts (used by the "short trip" rules)
CITY_REGIONS = {
    "delhi": "north", "new delhi": "north", "noida": "north", "gurgaon": "north",
    "chandigarh": "north", "lucknow": "north", "dehradun": "north",
    "jaipur": "north", "amritsar": "north", "kanpur": "north",
    "mumbai": "west", "pune": "west", "ahmedabad": "west", "surat": "west",
    "nagpur": "central", "bhopal": "central", "indore": "central",
    "raipur": "central", "jabalpur": "central",
    "bengaluru": "south", "bangalore": "south", "chennai": "south",
    "hyderabad": "south", "kochi": "south", "coimbatore": "south",
    "mysuru": "south", "mysore": "south",
    "kolkata": "east", "patna": "east", "bhubaneswar": "east",
    "ranchi": "east", "siliguri": "east",
    "guwahati": "northeast", "imphal": "northeast",
}
REGIONS = ["north", "west", "central", "south", "east", "northeast"]

# ----------------------------------------------------------------------------
# 2. Destination facts
#    budget = approximate PER-PERSON trip cost in INR (stay + food + local
#    travel for the recommended duration; excludes long-distance transport).
#    These are ILLUSTRATIVE estimates, not live prices.
#    image_url is optional; if empty/broken the app draws a generated card art.
# ----------------------------------------------------------------------------
def _d(id, name, state, region, emoji, desc, climates, types, interests,
       budget, duration_text, durations, companions, season, short_from,
       features=(), popularity=5, image_url=""):
    return dict(id=id, name=name, state=state, region=region, emoji=emoji,
                description=desc, climates=list(climates), types=list(types),
                interests=list(interests), budget=budget,
                duration_text=duration_text, durations=list(durations),
                companions=list(companions), season=season,
                short_from=list(short_from), features=list(features),
                popularity=popularity, image_url=image_url)

ALL = ["solo", "friends", "family", "couple"]
DESTINATIONS = [
    _d("manali", "Manali", "Himachal Pradesh", "north", "🏔️",
       "A lively Himalayan resort town known for snow, river valleys and adventure sports such as paragliding and rafting.",
       ["cold"], ["hill_station", "nature"], ["adventure", "mountains", "nature", "relaxation"],
       (8000, 18000), "4–6 days", ["medium", "long"], ALL, "Mar–Jun for pleasant weather; Dec–Feb for snow", ["north"], popularity=9),
    _d("shimla", "Shimla", "Himachal Pradesh", "north", "🚂",
       "A colonial-era hill station with toy-train rides, pine forests, the Mall Road and mountain views.",
       ["cold", "moderate"], ["hill_station", "city"], ["mountains", "culture", "relaxation", "nature"],
       (6000, 15000), "3–5 days", ["medium"], ["friends", "family", "couple"], "Mar–Jun and Dec–Jan", ["north"], popularity=8),
    _d("kasol", "Kasol", "Himachal Pradesh", "north", "🎒",
       "A laid-back Parvati Valley village loved by backpackers for treks, cafes and riverside camping.",
       ["cold", "moderate"], ["hill_station", "nature"], ["adventure", "mountains", "nature", "nightlife"],
       (5000, 12000), "3–5 days", ["medium"], ["solo", "friends", "couple"], "Mar–Jun and Sep–Nov", ["north"], popularity=7),
    _d("dharamshala", "Dharamshala", "Himachal Pradesh", "north", "🛕",
       "Home to McLeod Ganj, Tibetan culture, monasteries and Dhauladhar mountain views with easy treks like Triund.",
       ["cold", "moderate"], ["hill_station", "nature"], ["mountains", "culture", "nature", "adventure", "relaxation"],
       (6000, 14000), "3–5 days", ["medium"], ["solo", "friends", "family", "couple"], "Mar–Jun and Sep–Nov", ["north"], popularity=7),
    _d("rishikesh", "Rishikesh", "Uttarakhand", "north", "🧘",
       "The yoga capital on the Ganga, offering river rafting, bungee jumping, ashrams and evening aarti.",
       ["moderate", "warm"], ["nature", "city"], ["adventure", "culture", "relaxation", "nature"],
       (4000, 12000), "2–4 days", ["short", "medium"], ALL, "Feb–May and Sep–Nov", ["north"], popularity=8),
    _d("mussoorie", "Mussoorie", "Uttarakhand", "north", "☁️",
       "The 'Queen of Hills' with waterfalls, cable-car rides and misty views, easily reached for a weekend break.",
       ["cold", "moderate"], ["hill_station"], ["mountains", "nature", "relaxation"],
       (5000, 13000), "2–4 days", ["short", "medium"], ["friends", "family", "couple"], "Mar–Jun and Sep–Nov", ["north"], popularity=7),
    _d("nainital", "Nainital", "Uttarakhand", "north", "🛶",
       "A lake-centred hill town with boating, viewpoints and nearby forests and temples.",
       ["cold", "moderate"], ["hill_station", "nature"], ["nature", "mountains", "relaxation"],
       (5000, 13000), "2–4 days", ["short", "medium"], ["friends", "family", "couple"], "Mar–Jun and Sep–Nov", ["north"], popularity=7),
    _d("goa", "Goa", "Goa", "west", "🏖️",
       "India's best-known beach destination with sandy coastlines, Portuguese heritage, seafood and nightlife.",
       ["warm"], ["beach", "city"], ["beaches", "nightlife", "relaxation", "culture", "adventure"],
       (8000, 25000), "4–6 days", ["medium", "long"], ALL, "Nov–Feb", ["west", "south"], popularity=10),
    _d("gokarna", "Gokarna", "Karnataka", "south", "🌅",
       "A quieter coastal temple town with unspoilt beaches such as Om Beach and scenic coastal treks.",
       ["warm"], ["beach", "nature"], ["beaches", "relaxation", "nature", "culture", "adventure"],
       (5000, 12000), "3–5 days", ["medium"], ["solo", "friends", "couple"], "Oct–Mar", ["south", "west"], popularity=6),
    _d("munnar", "Munnar", "Kerala", "south", "🍃",
       "Rolling tea plantations, misty hills and wildlife nearby in the Western Ghats.",
       ["cold", "moderate"], ["hill_station", "nature"], ["nature", "mountains", "relaxation", "wildlife"],
       (8000, 18000), "3–5 days", ["medium"], ["family", "couple", "friends"], "Sep–Mar", ["south"], popularity=8),
    _d("ooty", "Ooty", "Tamil Nadu", "south", "🌹",
       "A classic Nilgiri hill station with botanical gardens, a heritage toy train and cool weather.",
       ["cold", "moderate"], ["hill_station", "nature"], ["nature", "mountains", "relaxation"],
       (6000, 15000), "3–5 days", ["medium"], ["family", "couple", "friends"], "Oct–Jun", ["south"], popularity=7),
    _d("coorg", "Coorg", "Karnataka", "south", "☕",
       "Coffee estates, waterfalls and misty hills, with trekking and homestay experiences.",
       ["moderate"], ["hill_station", "nature"], ["nature", "adventure", "relaxation", "wildlife"],
       (7000, 17000), "3–5 days", ["medium"], ["family", "couple", "friends", "solo"], "Oct–Mar", ["south"], popularity=7),
    _d("jaipur", "Jaipur", "Rajasthan", "north", "🏰",
       "The Pink City of forts, palaces and bazaars, with Amber Fort, City Palace and Hawa Mahal.",
       ["warm", "moderate"], ["city", "historical"], ["history", "culture", "nightlife"],
       (6000, 18000), "2–4 days", ["short", "medium"], ALL, "Oct–Mar", ["north", "west", "central"], popularity=9),
    _d("udaipur", "Udaipur", "Rajasthan", "west", "🏯",
       "The City of Lakes, famous for the City Palace, lakeside views and romantic sunsets.",
       ["warm", "moderate"], ["city", "historical"], ["history", "culture", "relaxation"],
       (8000, 22000), "3–4 days", ["short", "medium"], ["couple", "family", "friends"], "Oct–Mar", ["west", "north", "central"], popularity=8),
    _d("jaisalmer", "Jaisalmer", "Rajasthan", "west", "🐪",
       "The golden desert city with a living fort, havelis and camel safaris in the Thar Desert.",
       ["warm"], ["historical", "city"], ["history", "culture", "adventure"],
       (7000, 20000), "3–4 days", ["short", "medium"], ["friends", "couple", "family", "solo"], "Oct–Feb", ["west"], popularity=7),
    _d("varanasi", "Varanasi", "Uttar Pradesh", "north", "🪔",
       "One of the world's oldest living cities: Ganga ghats, evening aarti and deep spiritual culture.",
       ["warm", "moderate"], ["city", "historical"], ["history", "culture"],
       (4000, 12000), "2–4 days", ["short", "medium"], ["solo", "family", "friends"], "Oct–Mar", ["north", "east", "central"], popularity=8),
    _d("darjeeling", "Darjeeling", "West Bengal", "east", "🍵",
       "Tea gardens, the Darjeeling Himalayan Railway and sunrise views of Kanchenjunga.",
       ["cold", "moderate"], ["hill_station", "nature"], ["mountains", "nature", "culture", "relaxation"],
       (7000, 16000), "3–5 days", ["medium"], ["family", "couple", "friends"], "Mar–May and Oct–Nov", ["east", "northeast"], popularity=7),
    _d("gangtok", "Gangtok", "Sikkim", "northeast", "🌄",
       "Sikkim's capital with monasteries, cable cars and gateway access to high-altitude lakes and valleys.",
       ["cold", "moderate"], ["hill_station", "city", "nature"], ["mountains", "nature", "culture", "adventure"],
       (9000, 20000), "4–6 days", ["medium", "long"], ["family", "couple", "friends", "solo"], "Mar–Jun and Sep–Nov", ["northeast", "east"], popularity=7),
    _d("shillong", "Shillong", "Meghalaya", "northeast", "💧",
       "The 'Scotland of the East' with waterfalls, living-root bridges nearby and a lively music scene.",
       ["cold", "moderate"], ["hill_station", "nature"], ["nature", "adventure", "culture", "nightlife"],
       (8000, 18000), "4–6 days", ["medium", "long"], ["friends", "couple", "solo", "family"], "Oct–May", ["northeast", "east"], popularity=6),
    _d("andaman", "Andaman and Nicobar Islands", "Andaman & Nicobar (UT)", "east", "🏝️",
       "Clear-water island beaches such as Radhanagar, with scuba diving, snorkelling and marine life.",
       ["warm"], ["beach", "nature"], ["beaches", "adventure", "nature", "relaxation", "wildlife"],
       (25000, 55000), "5–7 days", ["long", "extended"], ["couple", "family", "friends"], "Oct–May", [], ["island"], popularity=8),
]
DEST_BY_ID = {d["id"]: d for d in DESTINATIONS}


def destination_facts(dest):
    """Describe a destination as a set of 'attribute:value' facts."""
    facts = set()
    facts.update("type:" + t for t in dest["types"])
    facts.update("interest:" + i for i in dest["interests"])
    facts.update("climate:" + c for c in dest["climates"])
    facts.update("companion:" + c for c in dest["companions"])
    facts.update("duration:" + d for d in dest["durations"])
    facts.update("short_trip_from:" + r for r in dest["short_from"])
    facts.update("feature:" + f for f in dest["features"])
    lowest = dest["budget"][0]
    facts.update("affordable:" + level for level, cap in BUDGET_CAPS.items() if lowest <= cap)
    return facts


# ----------------------------------------------------------------------------
# 3. IF-THEN production rules
#    "if"   : list of conditions, ALL must be in working memory.
#             A condition may list alternatives with '|'  (OR), e.g.
#             "budget:low|budget:very_low".
#    "then" : facts added to working memory when the rule fires.
#             Facts starting with "match:" are RECOMMENDATION facts: they say
#             "prefer destinations that have this attribute".
#             Other facts (e.g. "theme:...") are INTERMEDIATE facts that other
#             rules can use -> this is what makes the chaining happen.
#    "weight": importance of the match: facts produced by this rule.
# ----------------------------------------------------------------------------
RULES = []

def _rule(name, if_, then, because, weight=0):
    RULES.append({"id": "R%02d" % (len(RULES) + 1), "name": name, "if": if_,
                  "then": then, "weight": weight, "because": because})

# --- Layer 1: rules that read user facts and derive intermediate "themes" ---
_rule("Budget mountain trip",
      ["budget:low|budget:very_low", "climate:cold", "interest:mountains"],
      ["theme:budget_mountain"],
      "You want a low-budget trip to cold mountain areas.")
_rule("Beach holiday",
      ["interest:beaches", "climate:warm"],
      ["theme:beach_holiday"],
      "You like beaches and warm weather.")
_rule("Heritage trip",
      ["interest:history|interest:culture", "type:historical"],
      ["theme:heritage_trip"],
      "You are interested in history/culture and chose a historical destination.")
_rule("Family nature trip",
      ["companion:family", "interest:nature"],
      ["theme:family_nature"],
      "You are travelling with family and enjoy nature.")
_rule("Friends adventure trip",
      ["companion:friends", "interest:adventure"],
      ["theme:adventure_group"],
      "You are travelling with friends and want adventure.")
_rule("Couple getaway",
      ["companion:couple", "interest:relaxation"],
      ["theme:romantic_getaway"],
      "You are travelling as a couple and want to relax.")
_rule("Solo explorer",
      ["companion:solo", "interest:adventure|interest:culture|interest:nature"],
      ["theme:solo_explorer"],
      "You are travelling solo and want to explore.")
_rule("Island escape",
      ["duration:long|duration:extended", "interest:beaches"],
      ["theme:island_escape"],
      "A long trip with beach interest suits an island holiday.")

# --- Layer 2: rules that use intermediate themes (chained rules) ---
_rule("Beach holiday -> beach destinations", ["theme:beach_holiday"],
      ["match:type:beach"], "Beach holiday theme: beach destinations are preferred.", 5)
_rule("Budget mountain -> hill stations", ["theme:budget_mountain"],
      ["match:type:hill_station", "match:affordable:low"],
      "Budget mountain theme: affordable hill stations are preferred.", 3)
_rule("Heritage trip -> historical places", ["theme:heritage_trip"],
      ["match:type:historical"], "Heritage theme: historical destinations are preferred.", 4)
_rule("Family nature -> family-friendly", ["theme:family_nature"],
      ["match:companion:family", "match:type:nature"],
      "Family nature theme: family-friendly nature spots are preferred.", 3)
_rule("Adventure group -> adventure spots", ["theme:adventure_group"],
      ["match:interest:adventure", "match:companion:friends"],
      "Group adventure theme: adventure spots good for friends are preferred.", 3)
_rule("Couple getaway -> couple-friendly", ["theme:romantic_getaway"],
      ["match:companion:couple", "match:interest:relaxation"],
      "Couple getaway theme: relaxing, couple-friendly places are preferred.", 3)
_rule("Solo explorer -> solo-friendly", ["theme:solo_explorer"],
      ["match:companion:solo"],
      "Solo explorer theme: destinations suitable for solo travellers are preferred.", 3)
_rule("Island escape -> island destinations", ["theme:island_escape"],
      ["match:feature:island"],
      "Island escape theme: island destinations are preferred.", 3)

# --- Layer 3: a rule that chains on a chained fact ---
_rule("Romantic hills", ["theme:romantic_getaway", "climate:cold"],
      ["theme:honeymoon_hills"], "A couple getaway in a cold climate suggests hills.")
_rule("Honeymoon hills -> hill stations", ["theme:honeymoon_hills"],
      ["match:type:hill_station"], "Honeymoon-hills theme: hill stations are preferred.", 2)

# --- Rules for single preferences (generated from the vocabulary) ---
for _label, _key in BUDGET_OPTIONS.items():
    _rule("Budget " + _label, ["budget:" + _key], ["match:affordable:" + _key],
          "Your budget is %s per person, so destinations whose lowest approximate cost fits it are preferred." % _label, 3)
for _label, _key in CLIMATE_OPTIONS.items():
    if _key != "any":
        _rule("Climate " + _label, ["climate:" + _key], ["match:climate:" + _key],
              "You prefer a %s climate." % _key, 3)
for _label, _key in DURATION_OPTIONS.items():
    _rule("Duration " + _label, ["duration:" + _key], ["match:duration:" + _key],
          "Your trip length is %s." % _label, 2)
for _label, _key in INTEREST_OPTIONS.items():
    _rule("Interest " + _label, ["interest:" + _key], ["match:interest:" + _key],
          "You are interested in %s." % _label.lower(), 2)
for _label, _key in TYPE_OPTIONS.items():
    if _key != "any":
        _rule("Type " + _label, ["type:" + _key], ["match:type:" + _key],
              "You prefer a %s." % _label.lower(), 3)
for _label, _key in COMPANION_OPTIONS.items():
    _rule("Companions " + _label, ["companion:" + _key], ["match:companion:" + _key],
          "You are travelling: %s." % _label.lower(), 1)

# --- Short trip + starting city rule (generated per region) ---
for _region in REGIONS:
    _rule("Short trip from %s India" % _region,
          ["duration:short", "origin:" + _region],
          ["match:short_trip_from:" + _region],
          "Your trip is only 1–2 days and you start in %s India, so nearby destinations are prioritised." % _region, 4)


# ----------------------------------------------------------------------------
# 4. Plain browsing helper for the Destination Explorer (NOT an expert system)
# ----------------------------------------------------------------------------
def browse(query="", states=None, budget_key="any", category="any"):
    """Simple search + filter used by the Destination Explorer page."""
    out = []
    for d in DESTINATIONS:
        if query and query.strip().lower() not in d["name"].lower():
            continue
        if states and d["state"] not in states:
            continue
        if budget_key != "any" and d["budget"][0] > BUDGET_CAPS[budget_key]:
            continue
        if category != "any" and category not in d["types"]:
            continue
        out.append(d)
    return sorted(out, key=lambda x: x["name"])
