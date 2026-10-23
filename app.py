"""Multimodal Construction Intelligence Platform (Skill Wallet Capstone Project 1)."""
import json
import urllib.parse

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
.hero{padding:1.1rem 1.4rem;border-radius:14px;background:linear-gradient(120deg,#0f2027,#2c5364);color:#fff;margin-bottom:1rem}
.hero h1{margin:0;font-size:1.7rem}.hero p{margin:.2rem 0 0;opacity:.8}
.card{padding:.9rem 1rem;border-radius:12px;border:1px solid rgba(128,128,128,.25);background:rgba(128,128,128,.07)}
.card .v{font-size:1.6rem;font-weight:700}.card .l{font-size:.8rem;opacity:.7;text-transform:uppercase;letter-spacing:.04em}
.pill{display:inline-block;padding:.15rem .7rem;border-radius:999px;font-weight:600;font-size:.82rem;color:#fff}
</style>
""", unsafe_allow_html=True)

SEV_COLOR = {"Low": "#2e9e5b", "Medium": "#d9a400", "High": "#e8710a", "Critical": "#c62828",
             "Compliant": "#2e9e5b", "Needs Attention": "#d9a400", "Non-Compliant": "#c62828"}


def pill(text):
    return f'<span class="pill" style="background:{SEV_COLOR.get(text, "#546e7a")}">{text}</span>'


def card(label, value):
    st.markdown(f'<div class="card"><div class="l">{label}</div><div class="v">{value}</div></div>',
                unsafe_allow_html=True)


def inr(x):
    return f"₹{x / 1e7:.2f} Cr" if x >= 1e7 else f"₹{x / 1e5:.2f} Lakh"


# ---------------------------------------------------------------- AI layer
def get_model(api_key, model_name, json_mode=True, system=None):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    cfg = {"response_mime_type": "application/json"} if json_mode else None
    return genai.GenerativeModel(model_name, generation_config=cfg, system_instruction=system)


def analyze_image(prompt, image, demo_payload):
    """Run a multimodal prompt; fall back to demo data when no key or on error."""
    key = st.session_state.get("api_key")
    if not key:
        return demo_payload, True
    try:
        resp = get_model(key, st.session_state["model"]).generate_content([prompt, image])
        txt = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(txt), False
    except Exception as e:  # network, quota, parse errors
        st.warning(f"Gemini call failed ({e}). Showing demonstration output instead.")
        return demo_payload, True


PPE_PROMPT = """You are a construction safety auditor (OSHA 1926 and IS 456 / NBC India).
Analyse the site photo. Return ONLY JSON:
{"safety_score":0-100,"overall_status":"Compliant|Needs Attention|Non-Compliant",
"ppe_detection":{"helmet":bool,"high_vis_vest":bool,"steel_toe_boots":bool,"safety_harness":bool},
"workers_detected":int,
"hazards":[{"hazard":str,"severity":"Low|Medium|High|Critical","remedy":str}],
"summary":str}"""

CRACK_PROMPT = """You are a structural engineer. Analyse this concrete/wall surface. Return ONLY JSON:
{"defect_type":"Hairline|Settlement|Structural Shear|Thermal Expansion|Spalling",
"estimated_width_mm":float,"severity_score":0-100,"urgency":"Low|Medium|High|Critical",
"root_causes":[str],"recommended_repairs":[str],"monitoring_advice":str}"""

DEMO_PPE = {"safety_score": 62, "overall_status": "Needs Attention", "workers_detected": 3,
            "ppe_detection": {"helmet": True, "high_vis_vest": True, "steel_toe_boots": False, "safety_harness": False},
            "hazards": [
                {"hazard": "Worker at height without harness", "severity": "Critical",
                 "remedy": "Stop work at height; provide full-body harness anchored to a rated point."},
                {"hazard": "Open-toe footwear observed", "severity": "High",
                 "remedy": "Enforce steel-toe boots at site gate checks."},
                {"hazard": "Loose material near edge", "severity": "Medium",
                 "remedy": "Install toe boards and stack materials away from edges."}],
            "summary": "DEMO MODE: partial PPE compliance; fall-protection gaps need immediate action."}
DEMO_CRACK = {"defect_type": "Structural Shear", "estimated_width_mm": 2.8, "severity_score": 74,
              "urgency": "High",
              "root_causes": ["Differential settlement of footing", "Overloading of beam-column joint", "Inadequate shear reinforcement"],
              "recommended_repairs": ["Epoxy injection for crack sealing", "Structural re-grouting with non-shrink grout", "Jacketing of affected member after engineer review"],
              "monitoring_advice": "DEMO MODE: install tell-tale gauges and re-measure weekly for 8 weeks."}

# ---------------------------------------------------------------- Sidebar
with st.sidebar:
    st.header("🏗️ Control Panel")
    st.session_state["api_key"] = st.text_input("Google Gemini API Key", type="password",
                                                help="Leave empty for demonstration mode.")
    st.session_state["model"] = st.selectbox("Model", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
    st.success("Live AI mode") if st.session_state["api_key"] else st.info("Demonstration mode (no key)")
    st.divider()
    st.subheader("Architecture")
    st.markdown("""
- **Vision layer**: Gemini multimodal → JSON contracts
- **Rules engine**: cost & valuation model (INR)
- **Advisory**: weather protocols + chat assistant
- **Render**: Pollinations/Flux concept art
- **State**: Streamlit session only, no database
""")
    st.caption("Tabs: Safety · Cracks · Planning · Site Assistant")

st.markdown('<div class="hero"><h1>Multimodal Construction Intelligence Platform</h1>'
            '<p>Safety audits · Structural diagnostics · Cost & valuation · Weather-aware site advisory</p></div>',
            unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["🦺 Safety & PPE", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Site Assistant"])

# ---------------------------------------------------------------- Tab 1
with t1:
    up = st.file_uploader("Upload site photo", type=["jpg", "jpeg", "png"], key="ppe")
    if up:
        img = Image.open(up).convert("RGB")
        c1, c2 = st.columns([1, 1.3])
        c1.image(img, use_container_width=True)
        if c2.button("Run safety audit", type="primary"):
            with st.spinner("Analysing PPE compliance..."):
                st.session_state["ppe"], demo = analyze_image(PPE_PROMPT, img, DEMO_PPE)
        r = st.session_state.get("ppe")
        if r:
            with c2:
                m1, m2, m3 = st.columns(3)
                with m1: card("Safety score", f"{r.get('safety_score', 0)}/100")
                with m2: card("Workers", r.get("workers_detected", "–"))
                with m3: card("Status", "")
                st.markdown(pill(r.get("overall_status", "–")), unsafe_allow_html=True)
                st.progress(min(max(int(r.get("safety_score", 0)), 0), 100) / 100)
                st.write(r.get("summary", ""))
                st.markdown("**PPE checklist**")
                for k, v in r.get("ppe_detection", {}).items():
                    st.write(("✅ " if v else "❌ ") + k.replace("_", " ").title())
            st.markdown("### Identified hazards")
            for h in r.get("hazards", []):
                st.markdown(f"{pill(h.get('severity', 'Low'))} **{h.get('hazard')}** — {h.get('remedy')}",
                            unsafe_allow_html=True)
            st.download_button("⬇️ Download JSON report", json.dumps(r, indent=2), "safety_report.json",
                               "application/json")
    else:
        st.info("Upload a JPG/PNG of a construction site to begin.")

# ---------------------------------------------------------------- Tab 2
with t2:
    up = st.file_uploader("Upload concrete / wall surface", type=["jpg", "jpeg", "png"], key="crack")
    if up:
        img = Image.open(up).convert("RGB")
        c1, c2 = st.columns([1, 1.3])
        c1.image(img, use_container_width=True)
        if c2.button("Diagnose defect", type="primary"):
            with st.spinner("Classifying defect..."):
                st.session_state["crack"], _ = analyze_image(CRACK_PROMPT, img, DEMO_CRACK)
        r = st.session_state.get("crack")
        if r:
            with c2:
                a, b, c = st.columns(3)
                with a: card("Defect", r.get("defect_type", "–"))
                with b: card("Width", f"{r.get('estimated_width_mm', 0)} mm")
                with c: card("Severity", f"{r.get('severity_score', 0)}/100")
                st.markdown("Urgency: " + pill(r.get("urgency", "Low")), unsafe_allow_html=True)
                st.markdown("**Root causes**")
                for x in r.get("root_causes", []): st.write("• " + x)
                st.markdown("**Recommended repairs**")
                for x in r.get("recommended_repairs", []): st.write("🔧 " + x)
                st.info(r.get("monitoring_advice", ""))
            st.download_button("⬇️ Download JSON report", json.dumps(r, indent=2), "crack_report.json",
                               "application/json")
    else:
        st.info("Upload an image of a crack or damaged surface.")

# ---------------------------------------------------------------- Tab 3
RATES = {"Residential Villa": (2200, 1.15), "Apartment Block": (1900, 1.0),
         "Commercial Building": (2600, 1.25), "Industrial Warehouse": (1500, 0.7)}
TIER_COST = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.85}
TIER_MARKET = {"Tier 1": 9500, "Tier 2": 5500, "Tier 3": 3200}
MILESTONES = [(0, "Site prep"), (10, "Foundation"), (30, "Superstructure"), (60, "Masonry & MEP"),
              (85, "Finishing"), (100, "Handover")]

with t3:
    c1, c2 = st.columns(2)
    stype = c1.selectbox("Structure type", list(RATES))
    tier = c2.selectbox("Location tier", list(TIER_COST))
    sqft = c1.number_input("Built-up area (sq ft)", 200, 500000, 2000, 100)
    pct = c2.slider("Completion (%)", 0, 100, 40)
    base, mkt_factor = RATES[stype]
    budget = sqft * base * TIER_COST[tier]
    capex = budget * pct / 100
    full_value = sqft * TIER_MARKET[tier] * mkt_factor
    asset_value = full_value * (0.25 + 0.75 * pct / 100)  # land/approvals floor + progress
    steel_t, cement_bags = sqft * 4 / 1000, sqft * 0.4  # rule-of-thumb: 4 kg steel, 0.4 bag cement per sq ft

    m = st.columns(4)
    for col, (l, v) in zip(m, [("Total budget", inr(budget)), ("CapEx incurred", inr(capex)),
                               ("Current asset value", inr(asset_value)), ("Value on completion", inr(full_value))]):
        with col: card(l, v)
    m = st.columns(3)
    with m[0]: card("Steel required", f"{steel_t:.1f} tonnes")
    with m[1]: card("Cement required", f"{cement_bags:,.0f} bags")
    with m[2]: card("Value uplift at completion", inr(full_value - asset_value))
    st.markdown("#### Milestone progress")
    st.progress(pct / 100)
    done = [n for p, n in MILESTONES if pct >= p]
    st.write(" → ".join(f"**{n}**" if n == done[-1] else n for _, n in MILESTONES))
    st.caption("Estimates use indicative per-sq-ft rates and rule-of-thumb material ratios; validate with a QS.")

    st.markdown("#### Conceptual 3D rendering")
    style = st.text_input("Style notes", "modern, glass facade, landscaped garden, golden hour")
    if st.button("Generate concept render"):
        prompt = f"3D architectural render of a {stype.lower()}, {sqft} sq ft, Indian {tier} city, {style}, photorealistic"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=640&model=flux&nologo=true"
        st.image(url, caption="Generated via Pollinations (Flux)", use_container_width=True)
        st.code(prompt)

# ---------------------------------------------------------------- Tab 4
WEATHER = {
    "Normal": ("🟢", "Low", ["Standard PPE and toolbox talk.", "Routine inspection of scaffolds and lifting gear."]),
    "High Wind": ("🟠", "High", ["Suspend crane and tower-crane operations above rated wind limit.",
                                 "Secure sheeting, formwork and loose materials.", "Halt work on exposed scaffolds and edges."]),
    "Heavy Rain": ("🔵", "High", ["Isolate temporary electrical supply; use RCCB-protected circuits only.",
                                  "Cover fresh concrete; pause pours and check formwork drainage.",
                                  "Pump out excavations and inspect trench shoring."]),
    "Extreme Heat": ("🔴", "High", ["Schedule heavy work before 11 AM and after 4 PM; hydration breaks hourly.",
                                    "Wet-cure concrete for 7+ days, use curing compound and shade.",
                                    "Monitor workers for heat stress."]),
}
FALLBACK = {"curing": "Cure concrete at least 7 days (OPC), keeping it continuously moist; 10-14 days in hot weather.",
            "slump": "Typical slump is 25-100 mm for beams/columns and 100-150 mm for pumped concrete; confirm per IS 456 mix design.",
            "ppe": "Minimum PPE: helmet, high-vis vest, safety boots, gloves; harness above 1.8 m (OSHA) or 2 m per local code.",
            "crack": "Measure width and monitor; hairline cracks are mostly shrinkage, while cracks over ~2-3 mm or growing need an engineer."}

with t4:
    w = st.selectbox("Today's weather", list(WEATHER))
    icon, lvl, alerts = WEATHER[w]
    st.markdown(f"### {icon} {w} — risk {pill(lvl)}", unsafe_allow_html=True)
    for a in alerts:
        (st.success if w == "Normal" else st.warning)(a)

    st.markdown("---\n#### Engineering assistant")
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if q := st.chat_input("Ask about site safety, materials, curing, codes..."):
        st.session_state["chat"].append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.write(q)
        key = st.session_state.get("api_key")
        try:
            if not key:
                raise RuntimeError("demo")
            sys_p = (f"You are a senior civil/construction engineer in India. Today's site weather: {w}. "
                     "Be concise and practical; cite IS/OSHA codes where relevant.")
            hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state["chat"][:-1]]
            reply = get_model(key, st.session_state["model"], False, sys_p).start_chat(history=hist).send_message(q).text
        except Exception:
            reply = next((v for k, v in FALLBACK.items() if k in q.lower()),
                         f"(Demo mode) With {w.lower()} conditions, follow the alerts above. Add a Gemini key for full answers.")
        st.session_state["chat"].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)
    if st.session_state["chat"] and st.button("Clear chat"):
        st.session_state["chat"] = []
        st.rerun()
