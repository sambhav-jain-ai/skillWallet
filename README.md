# 🏗️ Multimodal Construction Intelligence Platform

A Streamlit decision-support app that analyses construction site photos, diagnoses concrete defects, estimates project cost and real estate value in INR, and gives weather-aware safety guidance.

Built as **Skill Wallet Capstone Project 1** (Generative AI | Real Estate Decision Support).

**🔗 Live demo:** `<paste your Streamlit app link here>`

<!-- Add a screenshot: upload it to the repo and use ![Screenshot](screenshot.png) -->

## Features

| Module | What it does |
|---|---|
| 🦺 **Site Safety & PPE Audit** | Upload a site photo. Gemini checks helmets, high-vis vests, boots and harnesses (OSHA / IS standards) and returns a structured JSON report with a safety score (0-100), status, hazards, severity and remedies. |
| 🧱 **Crack Diagnostics** | Upload a concrete or wall image. Classifies the defect (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling) with estimated width in mm, severity score, root causes, repairs and urgency. |
| 📐 **Planning & Valuation** | Enter structure type, built-up area, city tier and completion %. Calculates total budget, capex incurred, current and on-completion asset value (Lakhs/Crores), steel and cement requirement, milestone progress, and a conceptual 3D render via Pollinations (Flux). |
| 🌦️ **Site Assistant** | Weather-aware safety alerts (High Wind, Heavy Rain, Extreme Heat, Normal) and a multi-turn construction engineering chatbot. |

**Demo mode:** with no API key, the app runs with sample outputs so the full UI can be explored. Add a Google Gemini key in the sidebar for real analysis.

## Tech Stack

- Python 3.9+
- Streamlit
- Google Gemini (multimodal) via `google-generativeai`
- Pillow
- Pollinations AI (Flux) for concept renders
- JSON data contracts for all AI outputs
- No database; session state only

## Run Locally

```bash
git clone https://github.com/sambhav-jain-ai/skillWallet.git
cd skillWallet
pip install -r requirements.txt
streamlit run app.py
```

Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com) and paste it into the sidebar. Never commit your key to the repo.

## Deploy

Deployed on Streamlit Community Cloud: push `app.py` and `requirements.txt` to a public GitHub repo, then create a new app at [share.streamlit.io](https://share.streamlit.io) with `app.py` as the main file.

## Notes and Limitations

- Cost and valuation figures use indicative per-sq-ft rates and rule-of-thumb material ratios (about 4 kg steel and 0.4 bag cement per sq ft). They are estimates, not quotations; validate with a quantity surveyor.
- AI safety and crack assessments are decision support only and do not replace inspection by a qualified engineer or safety officer.

## Author

Sambhav Jain
