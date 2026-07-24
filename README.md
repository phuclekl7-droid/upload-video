<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=00c8ff&height=200&section=header&text=NEO%20Uploader&fontSize=70&fontAlignY=35&desc=Next-Gen%20Social%20Media%20Automation%20Engine&descAlignY=55&descAlign=50" width="100%" />

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge&logo=githubactions)](https://github.com)
[![Python Version](https://img.shields.io/badge/Python-3.10+-00c8ff?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Engine-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/)

**An end-to-end cybernetic automation system controlled via Telegram WebApp.**  
*Bypass API limitations. Simulate human intelligence. Distribute video assets globally.*

[Features](#-core-capabilities) • [Architecture](#-system-architecture) • [Setup](#-deployment) • [Usage](#-mission-control)

---
</div>

## 🌌 Core Capabilities

### ⚡ Neural Video Processing
- **Quantum Splitter**: Utilizes `ffmpeg` to parse and slice massive video files into optimal segments in milliseconds, without quality degradation (zero re-encoding).

### 🛡️ Phantom Automation (Playwright)
- **TikTok Studio Integration**: Dynamic DOM traversal to bypass popups, inject metadata (captions & hashtags), and auto-upload custom thumbnails.
- **Meta (Facebook) Network**: Seamless interaction with Facebook Creator Studio/Business Suite.
- **YouTube Mainframe**: Automated sequence execution for YouTube Studio.

### 🎛️ Command Center
- **Telegram WebApp UI**: A futuristic, responsive dashboard built directly into your Telegram client. Control uploads, track statuses, and split videos on the fly.
- **State Persistence**: Securely caches session cookies (`*_profile/`) to maintain permanent authentication tunnels.

---

## 🧬 System Architecture

```mermaid
graph TD
    classDef user fill:#0f172a,stroke:#00c8ff,stroke-width:2px,color:#fff;
    classDef bot fill:#1e1e1e,stroke:#f59e0b,stroke-width:2px,color:#fff;
    classDef engine fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef social fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#fff;

    U((💻 Commander)):::user -->|Trigger| B[🤖 Telegram Core Bot]:::bot
    B -->|Initialize| UI[🌐 WebApp Dashboard]:::bot
    
    subgraph Execution Matrix
        B -->|Payload| V[✂️ FFmpeg Slicer]:::engine
        V --> P1[🎥 Chunk 1]:::engine
        V --> P2[🎥 Chunk 2]:::engine
    end
    
    subgraph Phantom Uploaders
        P1 --> TK[🎵 TikTok Automation]:::social
        P1 --> FB[📘 Facebook Automation]:::social
        P1 --> YT[🔴 YouTube Automation]:::social
    end
    
    TK -->|Chromium Headless| TKS[TikTok Servers]
    FB -->|Chromium Headless| FBS[Meta Servers]
    YT -->|Chromium Headless| YTS[Google Servers]
```

---

## 💻 Deployment

```bash
# 1. Clone the repository into your local mainframe
git clone https://github.com/phuclekl7-droid/upload-video.git
cd upload-video

# 2. Install dependencies & initialize phantom browser drivers
pip install -r requirements.txt
playwright install chromium

# 3. Authenticate communication protocols (Run once)
python login_tiktok.py
python login_facebook.py
python login_youtube.py
```

## 🛰️ Mission Control

Ignite the primary bot process:
```bash
python bot.py
```

**Commands:**
- `/start` - Access the WebApp Matrix.
- `/split` - Activate the video slicer module.
- `/status` - Diagnostics and current operations.

---
<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=16&pause=1000&color=00C8FF&center=true&vCenter=true&width=435&lines=Initializing+Phantom+Browsers...;Bypassing+Social+Media+Firewalls...;Upload+Complete.+System+Standing+By." alt="Typing SVG" />
</div>
