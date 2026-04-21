# 📡 GEO Radar — AI Brand Visibility Audit

Streamlit-based tool that audits how top AI models (**ChatGPT**, **Gemini**, **Claude**) answer real insurance-domain questions, and measures whether a target brand (default: **ביטוח ישיר / Direct Insurance**) is mentioned — across answers, sources, and the models' own reasoning.

Built for the **Generative Engine Optimization (GEO)** hackathon.

---

## ✨ Features

- **Multi-model audit** — Queries 3 live AI models in parallel with grounding/web-search tools enabled.
- **Real citations** — Extracts the actual URLs each model used (not synthetic ones).
- **Thinking transparency** — Surfaces each model's reasoning process and search queries.
- **Brand Audit system prompt** — Forces models to explicitly list which brands they saw in sources vs. which they included in the final answer.
- **🧑‍⚖️ Cross-model judgment** — Claude acts as universal judge, scoring fairness and detecting bias in the other models' answers.
- **📝 Actionable content briefs** — Auto-generates SEO briefs (headline, outline, keywords, recommended platform) per content gap.
- **🆚 Before / After comparison** — Snapshot baseline and measure impact after publishing content.
- **📊 Executive summary** — CEO-level card with "Lost Impressions" estimate and top priority action.
- **Hebrew RTL UI** — Full Hebrew support with branded visuals.

---

## 🚀 Quick Start

### 1. Clone
```bash
git clone https://github.com/Tamar401/Hackathon-Geo-Radar.git
cd Hackathon-Geo-Radar
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env
# edit .env and paste your keys
```

Required:
- `GOOGLE_API_KEY` — [Get one](https://aistudio.google.com/apikey)
- `OPENAI_API_KEY` — [Get one](https://platform.openai.com/api-keys)
- `ANTHROPIC_API_KEY` — [Get one](https://console.anthropic.com/)

Optional:
- `TAVILY_API_KEY` — fallback search provider

### 4. Run
```bash
streamlit run app.py
```

---

## 🏗️ Architecture

```
User → Streamlit UI
         ↓
   run_chat_audit()  ← iterates 4 fixed insurance questions
         ↓
   ┌─────┬─────┬─────┐
   │ Gemini │ GPT-4 │ Claude │   (parallel web-search)
   └─────┴─────┴─────┘
         ↓
   extract answers + citations + thinking
         ↓
   Claude-as-Judge × 3   → cross-model scores
         ↓
   generate_content_brief() (if gap detected)
         ↓
   Dashboard + Executive Summary + Before/After
```

---

## 🧰 Tech stack

- **Python 3.10+**, **Streamlit**
- **google-genai** (Gemini 2.5 Flash with `google_search` tool)
- **openai** (o4-mini with `web_search` via Responses API)
- **anthropic** (Claude Sonnet 4 with `web_search_20250305` tool)
- **plotly** for gauge/visuals
- **python-dotenv** for config

---

## 📁 Project structure

```
├── app.py              # Main Streamlit app (single-file)
├── .env.example        # Template for API keys
├── .gitignore
├── requirements.txt
├── logo.png / logo.svg # Branding assets
└── README.md
```

---

## 🔒 Security

- **Never commit `.env`** — it's git-ignored.
- API keys are loaded at runtime from environment variables only.
- No telemetry; all analysis runs locally in your Streamlit session.

---

## 🎯 Built by

Team Hackathon-Geo-Radar — 2026.
