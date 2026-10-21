<div align="center">

![FrogPipe Autonomous SEO Engine](assets/frogpipe_banner_v2.png)

# 🐸 FrogPipe — Autonomous SEO Spider & Audit Engine

**The Billion-Dollar Autonomous SEO Crawler & Executive Intelligence Pipeline**  
*Architected & Engineered by [Al Hossain Rifat](https://r1fat.pages.dev)*

[![Proprietary License](https://img.shields.io/badge/License-Proprietary%20All%20Rights%20Reserved-red.svg)](LICENSE)
[![Engine](https://img.shields.io/badge/Screaming%20Frog-Headless%20CLI-brightgreen.svg)](https://www.screamingfrog.co.uk)
[![Portfolio](https://img.shields.io/badge/Architect-r1fat.pages.dev-blueviolet.svg)](https://r1fat.pages.dev)
[![Version](https://img.shields.io/badge/FrogPipe-Mark%202%20Production-00ff88.svg)](frogpipe.py)

</div>

---

## ⚡ Overview

**FrogPipe** is an enterprise-grade automated SEO spider pipeline built directly on top of the **Screaming Frog SEO Spider CLI**. It executes high-speed headless crawls on single domains or lead lists, sanitizes bloated crawls, and automatically packages the **11 Essential SEO Audit Datasets** + **Competitors Analysis Matrix** with **100% full data preservation** (zero columns dropped):

1. **Issues Overview** (`1_Issues.csv` — Executive Overview of all SEO issues, warnings, and opportunities)
2. **H1 Headings** (`2_H1.csv` — Primary H1 heading tags and character analysis)
3. **H2 Headings** (`3_H2.csv` — Secondary H2 structure and subheading analysis)
4. **Meta Description** (`4_Meta_Description.csv` — Page meta descriptions, character lengths, and SERP snippets)
5. **Meta Tags** (`5_Meta_Tags.csv` — Directives, meta robots, canonical tags, and keywords)
6. **Content & Depth** (`6_Content.csv` — Word counts, text ratios, and content depth analysis)
7. **ALL Page Titles** (`7_Page_Titles.csv` — Page title tags, character lengths, and pixel widths)
8. **Internal URLs** (`8_URLs.csv` — Complete list of internal crawlable URLs and status codes)
9. **Images & Assets** (`9_Images.csv` — Image assets, missing alt text, dimensions, and file sizes)
10. **Search Console Status** (`10_Search_Console_Status.csv` — Search console status / HTTP response codes)
11. **Canonicals** (`11_Canonicals.csv` — Canonical tag implementation and indexability signals)
12. **Competitors Matrix** (High-Impact VIP Benchmark Matrix with client green glow and rival red benchmarks)

Automated packaging generates a clean directory directly in the project root vault:  
`📁 audited_sites/SEO_<Website_Domain>/`

---

## 🚀 Features (Mark 2)

- 🐸 **Autonomous Headless Engine**: Directly drives `ScreamingFrogSEOSpiderCli.exe` with real-time percentage progress bar and URL counter.
- 🎨 **Top-Tier Executive Google Sheets Live Sync**: Pushes directly to Google Apps Script webhook with custom vibrant tab colors, cyber obsidian master headers, sticky frozen column headers, status code pill badges (200 green, 3xx blue, 4xx red), and wide un-mushed columns.
- 📊 **Offline Master Excel Workbook**: Automatically builds a matching `.xlsx` offline workbook with tab colors, sticky banners, and color-coded rows.
- 📁 **Audited Sites Vault**: Organizes all CSVs, JSON manifests, and Excel workbooks cleanly in `audited_sites/SEO_<domain>/`.
- ⚙️ **Persistent Config Engine**: Remembers installation paths and webhook URLs in `config.json`.
- 🛡️ **Airtight Proprietary Architecture**: Enterprise-grade engineering strictly protected by proprietary commercial licensing.

---

## 💻 Quick Start

### 1. Installation
```bash
git clone https://github.com/expgg/frogpipe-source.git
cd frogpipe-source
pip install -r requirements.txt
```

### 2. Execution
Run the interactive terminal:
```bash
python frogpipe.py
```

Or pass target domains directly via CLI:
```bash
python frogpipe.py --url https://r1fat.pages.dev
python frogpipe.py --url http://drstangale.com
```

---

## 🌐 Google Sheets Webhook Deployment

To deploy the **High-Grade Executive Google Sheets Engine**:
1. Open [Google Apps Script](https://script.google.com).
2. Create a **New Project**.
3. Replace `Code.gs` with the contents of [`templates/code.gs`](templates/code.gs).
4. Click **Deploy > Manage deployments > Edit > New version > Deploy**.
5. Copy the Web App URL and paste it into [`config.json`](config.json) under `"sheet_webhook_url"`.

---

## 🔒 License & Intellectual Property

**COPYRIGHT (C) 2026 AL HOSSAIN RIFAT. ALL RIGHTS RESERVED.**

This software is strictly proprietary and confidential. No part of this codebase may be copied, modified, redistributed, forked, sublicensed, or used for commercial purposes without explicit, written permission executed directly by the author.

For inquiries, permissions, or custom software architecture:  
🌐 **Portfolio & Contact**: [r1fat.pages.dev](https://r1fat.pages.dev)
