# 🔍 Code Assistant — AI Code Explainer

> Paste any code → Understand every line → Know exactly how to run it.

Built with **Streamlit** + **Groq LLaMA 3.1** (free API).

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🔮 **AI Language Auto-Detection** — Automatically detects any programming language (Python, Java, JavaScript, TypeScript, C++, Rust, Go, SQL, HTML, CSS, Bash, PHP, etc.) without manual selection
- 📋 **Code Summary** — What the code does in plain English
- 🔍 **Step-by-Step Breakdown** — Every line explained in simple terms
- ▶️ **Run Instructions** — Exact terminal commands to execute
- ⚠️ **Bug Warnings** — Potential issues flagged
- 🛡️ **Anti-Hallucination Engine** — Deterministic AST parsing + greedy decoding (temperature=0.0) + dual-pass self-reflection verifier
- 💬 **Interactive Code Q&A Chat** — Ask follow-up questions, request optimizations, or ask for code changes in real time
- 🎨 **Custom Dark UI** — Teal/cyan accent theme, animated background
- ☁️ **Streamlit Cloud Ready** — Deploy in one click

---

## 🚀 Quick Start (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/code-assistant.git
cd code-assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
```bash
cp env.example .env
# Then edit .env and paste your key
```
Get a **free** key at → [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as main file
4. Go to **Settings → Secrets** and add:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy** ✅

---

## 📁 Project Structure

```
code-assistant/
├── app.py                      # Main Streamlit UI
├── explainer.py                # Groq API + prompt logic
├── requirements.txt            # Dependencies (3 packages only)
├── .gitignore
├── env.example                 # Template for local API key
└── .streamlit/
    ├── config.toml             # Dark theme config
    └── secrets.toml.example    # Streamlit Cloud secrets template
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit + Custom CSS |
| LLM | Groq API (LLaMA 3.1 70B) |
| Language | Python 3.9+ |
| Deployment | Streamlit Cloud |

---

## 📦 Size

Total repo size: **< 50 KB** (well under any limit)

---

## 📄 License

MIT — free to use, modify, and distribute.
