# 🚀 CAMORRO v1.1

> Social-Engineering Framework — Phishing simulation for **authorized** security assessments & Red Team exercises.
> Successor of the classic zphisher approach, rebuilt from scratch with a clean multi-step capture engine.

![python](https://img.shields.io/badge/Python-3.8%2B-blue)
![stdlib](https://img.shields.io/badge/deps-Standard%20Library%20Only-brightgreen)

---

## ✨ Features

- 🎯 **Multi-template engine** — Instagram, Facebook, Google, Generic + custom (DHL included)
- 💳 **Multi-step capture** — Card page → OTP page → Approve page (each step logged separately)
- 🖥️ **Live terminal output** — captured data appears in a formatted box in the terminal, with an alert beep
- 💾 **JSONL logging** — everything saved to `logs/<site>.jsonl` (IP, User-Agent, timestamp, step, data)
- 🌐 **4 tunnel providers** — cloudflared · ngrok · serveo · localhost.run
- 🎭 **Link masking** — `https://dhl.com-secure-xxxxx@tunnel` style + optional is.gd shortener
- 🧩 **No pip dependencies** — 100% Python standard library
- 📦 **Auto-generating templates** — built-in templates are written to `sites/` on first run

---

## 📋 Requirements

| Dependency | Purpose | Required |
|---|---|---|
| Python 3.8+ | Core engine | ✅ |
| cloudflared | Cloudflare tunnel | optional (recommended) |
| ngrok | ngrok tunnel | optional |
| ssh | serveo / localhost.run tunnels | optional |

---

## 🛠️ Installation

```bash
git clone https://github.com/Instagram1l/Instagram.git
cd Instagram
chmod +x install.sh
./install.sh          # checks python3, installs cloudflared, prepares dirs
