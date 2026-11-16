"""
app.py  --  Streamlit FRONTEND of TravelMate.
It only handles display and user input; all reasoning is done by
inference_engine.py using the knowledge in knowledge_base.py.
Run with:  streamlit run app.py
"""
import base64
import html as H
import streamlit as st

from knowledge_base import (BUDGET_OPTIONS, CLIMATE_OPTIONS, DURATION_OPTIONS, INTEREST_OPTIONS,
                            COMPANION_OPTIONS, TYPE_OPTIONS, DESTINATIONS, RULES, browse)
from inference_engine import recommend

st.set_page_config(page_title="TravelMate – Destination Expert System", page_icon="🧭", layout="wide")

NAVY, BLUE, LIGHT, ACCENT = "#0B1F3A", "#2E86DE", "#E8F3FD", "#F4A261"
st.markdown(f"""<style>
.block-container {{max-width: 1150px; padding-top: 1.5rem;}}
h1,h2,h3 {{color:{NAVY};}}
.hero {{background: linear-gradient(135deg,{NAVY} 0%,#1B4F8A 60%,{BLUE} 100%); color:white;
        padding:3rem 2rem; border-radius:18px; margin-bottom:1.2rem;}}
.hero h1 {{color:white; font-size:2.6rem; margin:0 0 .5rem 0;}}
.hero p {{font-size:1.1rem; opacity:.92; max-width:640px;}}
.brand {{font-weight:800; font-size:1.5rem; color:{NAVY};}}
.brand span {{color:{BLUE};}}
.card {{background:white; border:1px solid #DCE6F2; border-radius:14px; overflow:hidden;
        box-shadow:0 2px 10px rgba(11,31,58,.07); margin-bottom:1rem;}}
.card img {{width:100%; height:170px; object-fit:cover; display:block;}}
.card .body {{padding:.9rem 1rem 1rem 1rem;}}
.card h4 {{margin:0; color:{NAVY};}}
.sub {{color:#5B6B80; font-size:.88rem; margin-bottom:.4rem;}}
.tag {{display:inline-block; background:{LIGHT}; color:{NAVY}; border-radius:20px;
       padding:2px 10px; margin:2px 3px 2px 0; font-size:.78rem;}}
.badge {{background:{ACCENT}; color:{NAVY}; font-weight:700; border-radius:20px; padding:3px 12px; font-size:.85rem;}}
.bar {{background:#E3ECF6; border-radius:8px; height:10px; margin:.4rem 0;}}
.bar div {{background:{BLUE}; height:10px; border-radius:8px;}}
.flow {{display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; justify-content:center; margin:1rem 0;}}
.flow .box {{background:{NAVY}; color:white; padding:.8rem 1rem; border-radius:12px; text-align:center;
             min-width:150px; font-weight:600; font-size:.92rem;}}
.flow .box small {{display:block; font-weight:400; opacity:.8;}}
.flow .arrow {{font-size:1.6rem; color:{BLUE};}}
.note {{background:#FFF6EC; border-left:4px solid {ACCENT}; padding:.6rem .9rem; border-radius:6px; margin:.5rem 0;}}
.stButton>button, .stFormSubmitButton>button {{background:{BLUE}; color:white; border:0; border-radius:10px; font-weight:600;}}
</style>""", unsafe_allow_html=True)

LEVEL_LABEL = {v: k for k, v in BUDGET_OPTIONS.items()}


# ------------------------------- helpers -------------------------------------
def fallback_image(dest):
    """Generated SVG art, used when no image URL is set or the URL fails."""
    hue = sum(ord(c) for c in dest["name"]) % 360
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='600' height='340'>"
           f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
           f"<stop offset='0' stop-color='hsl({hue},60%,28%)'/><stop offset='1' stop-color='hsl({(hue+50)%360},70%,55%)'/>"
           f"</linearGradient></defs><rect width='600' height='340' fill='url(#g)'/>"
           f"<text x='300' y='175' font-size='96' text-anchor='middle'>{dest['emoji']}</text>"
           f"<text x='300' y='265' font-size='34' fill='white' text-anchor='middle' font-family='sans-serif' font-weight='bold'>{H.escape(dest['name'])}</text></svg>")
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def image_tag(dest):
    fb = fallback_image(dest)
    src = dest["image_url"] or fb
    return f'<img src="{src}" alt="{H.escape(dest["name"])}" onerror="this.onerror=null;this.src=\'{fb}\';">'


def money(n):
    return "₹{:,}".format(n)


def tags(items):
    return "".join(f'<span class="tag">{H.escape(str(i).replace("_", " ").title())}</span>' for i in items)


def dest_card(dest, extra=""):
    st.markdown(
        f'<div class="card">{image_tag(dest)}<div class="body"><h4>{H.escape(dest["name"])}</h4>'
        f'<div class="sub">{H.escape(dest["state"])} · ≈ {money(dest["budget"][0])}–{money(dest["budget"][1])} per person</div>'
        f'{tags(dest["types"])}{extra}</div></div>', unsafe_allow_html=True)


def go(page):
    st.session_state["page"] = page


def show_details(dest):
    c1, c2 = st.columns([1, 1.4])
    c1.markdown(f'<div class="card">{image_tag(dest)}</div>', unsafe_allow_html=True)
    c2.markdown(f"**{dest['name']}, {dest['state']}**  \n{dest['description']}")
    c2.markdown(
        f"- **Approximate budget:** {money(dest['budget'][0])}–{money(dest['budget'][1])} per person (illustrative estimate, not a live price; excludes long-distance transport)\n"
        f"- **Recommended duration:** {dest['duration_text']}\n"
        f"- **Climate:** {', '.join(dest['climates']).title()}\n"
        f"- **Best season (general):** {dest['season']}\n"
        f"- **Suitable for:** {', '.join(c.title() for c in dest['companions'])}")
    c2.markdown(tags(dest["interests"]), unsafe_allow_html=True)


# --------------------------------- pages -------------------------------------
def page_home():
    st.markdown('<div class="hero"><h1>Find Your Perfect Destination.</h1>'
                '<p>TravelMate is a rule-based Expert System. Tell it your budget, climate, interests and companions; '
                'its inference engine fires IF-THEN rules and recommends Indian destinations, explaining every choice.</p></div>',
                unsafe_allow_html=True)
    st.button("Discover Destinations", on_click=go, args=("Find Destinations",), type="primary")
    st.subheader("Featured Indian destinations")
    featured = sorted(DESTINATIONS, key=lambda d: -d["popularity"])[:6]
    cols = st.columns(3)
    for i, d in enumerate(featured):
        with cols[i % 3]:
            dest_card(d)
    st.subheader("How the Expert System works")
    c = st.columns(3)
    c[0].markdown("**1. Facts**  \nYour answers become facts such as `budget:low` or `interest:beaches`.")
    c[1].markdown("**2. Forward chaining**  \nRules like *IF beaches AND warm THEN beach holiday* fire repeatedly, creating new facts until nothing new can be derived.")
    c[2].markdown("**3. Ranked, explained results**  \nDerived facts are matched against the destination knowledge base, and each result shows the rules behind it.")


def page_find():
    st.header("Tell us about your trip")
    with st.form("prefs"):
        c1, c2 = st.columns(2)
        budget = c1.selectbox("Budget (per person)", list(BUDGET_OPTIONS), index=1)
        climate = c2.selectbox("Preferred climate", list(CLIMATE_OPTIONS), index=3)
        duration = c1.selectbox("Travel duration", list(DURATION_OPTIONS), index=1)
        companion = c2.selectbox("Travel companions", list(COMPANION_OPTIONS), index=1)
        dtype = c1.selectbox("Preferred destination type", list(TYPE_OPTIONS), index=0)
        city = c2.text_input("Starting city (optional)", placeholder="e.g. Delhi, Indore, Bengaluru")
        interests = st.multiselect("Travel interests (choose any)", list(INTEREST_OPTIONS))
        submitted = st.form_submit_button("Find my destinations")
    if submitted:
        prefs = {"budget": BUDGET_OPTIONS[budget], "climate": CLIMATE_OPTIONS[climate],
                 "duration": DURATION_OPTIONS[duration], "companion": COMPANION_OPTIONS[companion],
                 "dest_type": TYPE_OPTIONS[dtype], "start_city": city,
                 "interests": [INTEREST_OPTIONS[i] for i in interests]}
        with st.spinner("Running the inference engine..."):
            st.session_state["result"] = recommend(prefs)
        st.success("Done! Recommendations are shown below. Change the form above and search again any time.")
    result = st.session_state.get("result")
    if result:
        show_results(result)
    else:
        st.info("Fill in the form and press **Find my destinations**. Leaving fields at their defaults is fine.")


def show_results(result):
    st.header("Your recommendations")
    for n in result["notes"]:
        st.markdown(f'<div class="note">ℹ️ {H.escape(n)}</div>', unsafe_allow_html=True)
    st.caption("Match score = share of the rule-derived preference weight a destination satisfies. "
               "It is a rule-based score, **not a probability**. Budgets are approximate per-person estimates, not live prices.")
    for rank, rec in enumerate(result["recommendations"], 1):
        d = rec["destination"]
        left, right = st.columns([1, 2])
        left.markdown(f'<div class="card">{image_tag(d)}</div>', unsafe_allow_html=True)
        pct = rec["score_pct"]
        badge = f'<span class="badge">Rule-based match: {pct}%</span>' if pct is not None else ""
        right.markdown(
            f"### #{rank} {H.escape(d['name'])} <span class='sub'>· {H.escape(d['state'])}</span>  {badge}"
            f"<div class='bar'><div style='width:{pct or 0}%'></div></div>"
            f"<p>{H.escape(d['description'])}</p>"
            f"<p><b>Approx. budget:</b> {money(d['budget'][0])}–{money(d['budget'][1])} per person (illustrative) &nbsp; "
            f"<b>Duration:</b> {d['duration_text']} &nbsp; <b>Climate:</b> {', '.join(d['climates']).title()}<br>"
            f"<b>Best season:</b> {H.escape(d['season'])}</p>"
            f"{tags(d['interests'])}", unsafe_allow_html=True)
        with right.expander("Why this destination?"):
            for m in rec["matched"]:
                st.markdown(f"✅ **{m['text']}** — {m['reason']} _(rules: {', '.join(m['rules'])})_")
            for m in rec["missed"]:
                st.markdown(f"❌ {m['text']} — not satisfied by {d['name']}")
            st.caption(f"Score: {rec['score_points']} of {rec['max_points']} possible rule-weight points.")
    if result["alternatives"]:
        st.subheader("Alternative destinations")
        cols = st.columns(len(result["alternatives"]))
        for col, rec in zip(cols, result["alternatives"]):
            with col:
                dest_card(rec["destination"], f'<div class="sub">Rule-based match: {rec["score_pct"]}%</div>')
    with st.expander("Inference trace: facts and rules fired (forward chaining)"):
        st.markdown("**Initial facts:** " + ", ".join(f"`{f}`" for f in result["initial_facts"]))
        st.markdown("**Rules fired, in order:**")
        for r in result["fired_rules"]:
            cond = " AND ".join(r["if"])
            st.markdown(f"- **{r['id']} {r['name']}** (cycle {r['cycle']}): IF `{cond}` THEN {', '.join('`'+t+'`' for t in r['then'])}")
        st.markdown("**New facts derived:** " + (", ".join(f"`{f}`" for f in result["derived_facts"]) or "none"))


def page_explore():
    st.header("Destination Explorer")
    st.caption("Plain search and filters (no expert-system inference on this page).")
    c = st.columns(4)
    q = c[0].text_input("Search by name")
    states = c[1].multiselect("State", sorted({d["state"] for d in DESTINATIONS}))
    bud = c[2].selectbox("Budget", ["Any"] + list(BUDGET_OPTIONS))
    cat = c[3].selectbox("Category", list(TYPE_OPTIONS))
    found = browse(q, states, "any" if bud == "Any" else BUDGET_OPTIONS[bud], TYPE_OPTIONS[cat])
    if not found:
        st.warning("No destinations match these filters. Try removing one.")
        return
    st.write(f"**{len(found)}** destination(s) found")
    cols = st.columns(3)
    for i, d in enumerate(found):
        with cols[i % 3]:
            dest_card(d)
            with st.expander("View details"):
                show_details(d)


def page_about():
    st.header("About the Expert System")
    st.markdown("""
**Expert System** – a program that imitates the decision-making of a human expert using stored knowledge and rules rather than learning from data.

**Knowledge base** – the stored knowledge: facts about 20 destinations and %d IF-THEN production rules (`knowledge_base.py`).

**Inference engine** – the reasoning program that applies the rules to the user's facts (`inference_engine.py`).

**Forward chaining** – start with known facts, fire every rule whose IF part is true, add its conclusions as new facts, and repeat until no new facts appear. Each rule fires at most once, so the loop always stops.

**Explanation facility** – every recommendation lists the rules and facts behind it.
""" % len(RULES))
    st.markdown("""<div class="flow">
<div class="box">User Input<small>form answers</small></div><div class="arrow">→</div>
<div class="box">Knowledge Base<small>facts + rules</small></div><div class="arrow">→</div>
<div class="box">Inference Engine<small>forward chaining</small></div><div class="arrow">→</div>
<div class="box">Rule Evaluation<small>match + score</small></div><div class="arrow">→</div>
<div class="box">Recommendation<small>with explanation</small></div></div>""", unsafe_allow_html=True)
    st.subheader("Worked example")
    st.markdown("""
User facts: `interest:beaches`, `climate:warm`, `budget:medium`

1. **Cycle 1:** Rule *Beach holiday*: IF `interest:beaches` AND `climate:warm` THEN `theme:beach_holiday` (new fact).
2. **Chained rule:** *Beach holiday → beach destinations*: IF `theme:beach_holiday` THEN `match:type:beach`. This rule could not fire until the first one created its fact.
3. **Stop:** a full pass fires nothing new.
4. **Matching:** destinations with `type:beach` (Goa, Gokarna, Andaman) gain points; the best-scoring ones are shown with the rules that supported them.

**Honest note:** forward chaining produces the derived `match:` facts. The final percentage is a simple weighted count of how many of those facts a destination satisfies.
""")
    with st.expander("Browse all production rules"):
        for r in RULES:
            st.markdown(f"**{r['id']} {r['name']}** — IF `{' AND '.join(r['if'])}` THEN {', '.join('`'+t+'`' for t in r['then'])}")


# ------------------------------- navigation ----------------------------------
PAGES = {"Home": page_home, "Find Destinations": page_find,
         "Destination Explorer": page_explore, "About Expert System": page_about}
st.session_state.setdefault("page", "Home")
top = st.columns([1, 3])
top[0].markdown('<div class="brand">🧭 Travel<span>Mate</span></div>', unsafe_allow_html=True)
top[1].radio("Navigation", list(PAGES), key="page", horizontal=True, label_visibility="collapsed")
st.divider()
PAGES[st.session_state["page"]]()
st.divider()
st.caption("TravelMate is a college AI project. Budgets and seasons are general, approximate guidance; always check current prices, weather and availability before booking.")
