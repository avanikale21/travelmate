# 🧭 TravelMate – Travel Destination Recommendation Expert System

A college-level AI project: a rule-based expert system (knowledge base + IF-THEN rules + forward-chaining inference engine + explanation facility) with a Streamlit frontend. Focus: Indian destinations (20 included). No paid APIs or keys needed.

## File guide
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI: Home, Find Destinations, Destination Explorer, About Expert System |
| `knowledge_base.py` | Destination facts, vocabulary, and all IF-THEN production rules |
| `inference_engine.py` | Forward chaining, matching, ranking, explanations |
| `tests/test_inference_engine.py` | Automated unit tests (unittest) |
| `requirements.txt` | Dependencies |
| `.streamlit/config.toml` | Theme colours |

## How the expert system works
1. Form answers → facts (e.g. `budget:low`, `interest:beaches`).
2. **Forward chaining** (`forward_chain`) fires rules whose conditions are in working memory, adding new facts (e.g. `theme:beach_holiday`, then `match:type:beach`) until nothing new is derived. Each rule fires once, so it always terminates.
3. The derived `match:` facts are compared with each destination's attributes and a **rule-based match score** (weighted share, *not* a probability) is computed.
4. Each result lists which rules and facts support it, and what it missed.

Budgets are illustrative per-person estimates, not live prices. Images are generated card art by default; set `image_url` in `knowledge_base.py` for real photos (the app falls back automatically if a URL fails).

To add a destination, append a `_d(...)` entry to `DESTINATIONS`. To add a rule, call `_rule(...)`. International destinations need only new entries (and city/region vocabulary if desired).

## Run locally
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
python -m unittest discover -s tests -v            # run tests
```

## Upload to GitHub
```bash
git init
git add .
git commit -m "TravelMate expert system"
git branch -M main
# create an empty repo named travelmate on github.com, then:
git remote add origin https://github.com/<your-username>/travelmate.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub (authorise access to your repo).
2. Click **Create app** → choose your `travelmate` repo, branch `main`, main file `app.py`.
3. Click **Deploy**. After a minute you get a public `*.streamlit.app` URL.
