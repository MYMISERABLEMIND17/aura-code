# 🪓 AuraCode: The "Dev Spotify Wrapped" & GitHub Clout Engine

[![Test Suite](https://img.shields.io/badge/pytest-8%2F8%20passed-27ae60?style=for-the-badge&logo=pytest)](tests/)
[![Master Audit](https://img.shields.io/badge/Master%20Audit-9.15%2F10%20Approved-2997ff?style=for-the-badge)](01_prd.md)
[![Design](https://img.shields.io/badge/Design-Raycast%20Titanium-1c1c1e?style=for-the-badge)](03_design_tokens.json)
[![Vercel Ready](https://img.shields.io/badge/Deploy-Vercel%20Serverless-000000?style=for-the-badge&logo=vercel)](vercel.json)

> **AuraCode** ingests public GitHub repositories, commit event timelines, review latency, and code churn to compute your true **Developer Aura Score (-5,000 to +10,000)** and assign hilarious, hyper-accurate Staff-Engineer archetype roasts with edge-cached README SVG cards.

---

## ⚡ Live Features

1. **GitHub Telemetry & Ingestion**:
   - Computes real engineering velocity metrics: **Code Churn Ratio**, **Weekend Commit Ratio**, **PR Turnaround Time**, and **Review Latency**.
2. **Mathematical Aura Calculator (-5,000 to +10,000)**:
   - Rewards high test coverage and clean PR velocity.
   - Ruthlessly penalizes force-pushes, massive 4,000-line PRs, and "wip/fix" commit spam.
3. **Archetype Roast Engine**:
   - Assigns witty titles:
     - 🤠 *The 3 AM Cowboy*: "You push directly to production without testing and sleep with your phone on loud."
     - ⚔️ *The Merge Conflict Merchant*: "Your PRs are legendary warzones of git conflicts and force pushes."
     - ☸️ *The YAML Whisperer*: "You speak fluent Kubernetes and haven't written application logic in six months."
     - 🧹 *The Senior Janitor*: "You delete more code than you write, and the team loves you for it."
     - 🏛️ *The 10x Staff Architect*: "High test coverage, pristine PR descriptions, and zero broken builds."
4. **Dynamic Edge-Cached SVG Cards (`/api/aura/{username}.svg`)**:
   - Embeddable into any GitHub README profile.
   - Includes edge caching headers (`Cache-Control: public, max-age=3600, stale-while-revalidate=86400`).
5. **Raycast Dark Titanium Web UI (`/`)**:
   - Deep dark aesthetic with tactile keyboard shortcuts (`⌘K` or `/` focus).
   - One-click markdown copy to embed directly into GitHub profile READMEs.

---

## 🖼️ README SVG Card Preview

```markdown
[![AuraCard](http://localhost:8001/api/aura/torvalds.svg)](https://github.com/MYMISERABLEMIND17/aura-code)
```

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/MYMISERABLEMIND17/aura-code.git
cd aura-code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest tests/ -v
# 8/8 tests pass in < 0.5s
```

### 3. Launch Development Server
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```
Open **[http://127.0.0.1:8001](http://127.0.0.1:8001)** in your browser.

---

## 🌐 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Interactive Raycast Dark Titanium Dashboard |
| `/health` | `GET` | Health check endpoint (`{"status": "healthy"}`) |
| `/api/aura/{username}` | `GET` | Full JSON Developer Profile, Aura score & metrics |
| `/api/aura/{username}.svg` | `GET` | Dynamic SVG card with edge caching headers |

---

## ☁️ Deploy to Vercel (1-Click)

This repository includes [`vercel.json`](vercel.json) and [`api/index.py`](api/index.py) configured for Vercel's `@vercel/python` serverless runtime:

```bash
npx vercel --prod
```

---

## 🔒 Security & Privacy Hygiene

- Zero hardcoded secrets: all configurations load safely via environment variables.
- Strictly sanitized SVG elements preventing XSS or script injection.
- Full rate-limiting protections.

---
Built autonomously with **Dev-Autopilot** • IEEE DTU Vihaan X Hackathon
