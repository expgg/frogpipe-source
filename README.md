<div align="center">

![FrogPipe Autonomous SEO Engine](assets/frogpipe_banner_v2.png)

# 🐸 FrogPipe — Autonomous SEO Spider & Audit Engine

**The Billion-Dollar Autonomous SEO Crawler & 9-Data Intelligence Pipeline**  
*Architected & Engineered by [Al Hossain Rifat](https://r1fat.pages.dev)*

[![Proprietary License](https://img.shields.io/badge/License-Proprietary%20All%20Rights%20Reserved-red.svg)](LICENSE)
[![Engine](https://img.shields.io/badge/Screaming%20Frog-Headless%20CLI-brightgreen.svg)](https://www.screamingfrog.co.uk)
[![Portfolio](https://img.shields.io/badge/Architect-r1fat.pages.dev-blueviolet.svg)](https://r1fat.pages.dev)
[![Version](https://img.shields.io/badge/FrogPipe-Mark%201%20Production-00ff88.svg)](frogpipe.py)

</div>

---

## ⚡ Overview

**FrogPipe** is an enterprise-grade automated SEO spider pipeline built directly on top of the **Screaming Frog SEO Spider CLI**. It executes high-speed headless crawls on single domains or lead lists, sanitizes bloated crawls, and automatically packages the **9 Essential SEO Audit Datasets** into teacher-compliant deliverable bundles:

1. **Issues Overview** (`issues_overview_report.csv` ➔ `1_Issues.csv`)
2. **H1 + H2 Headings** (`h1_all.csv` + `h2_all.csv` ➔ `2_H1_H2.csv` *unified on Address*)
3. **Meta Tags & Descriptions** (`meta_description_all.csv` ➔ `3_Meta_Tags_Description.csv`)
4. **Content & Word Counts** (`content_all.csv` ➔ `4_Content.csv`)
5. **Page Titles** (`page_titles_all.csv` ➔ `5_Page_Titles.csv`)
6. **URLs & Response Status** (`internal_all.csv` ➔ `6_URLs.csv`)
7. **Images & Alt Attributes** (`images_all.csv` ➔ `7_Images.csv`)
8. **Search Console / Status Codes** (`search_console_all.csv` / `response_codes_all.csv` ➔ `8_Search_Console_Status.csv`)
9. **Canonicals** (`canonicals_all.csv` ➔ `9_Canonicals.csv`)

Automated packaging generates a clean directory directly on the user's Desktop:  
`📁 Desktop/SEO_<Website_Domain>/`

---

## 🚀 Features (Mark 1)

- 🐸 **Autonomous Headless Engine**: Directly drives `ScreamingFrogSEOSpiderCli.exe`.
- 📁 **Automated Desktop Bundling**: Auto-creates `SEO_<Domain>` with verified CSV outputs and `audit_manifest.json`.
- ⚙️ **Persistent Config Engine**: Auto-detects custom installation paths and remembers them in `config.json`.
- 🎨 **Executive Cyberpunk Terminal**: High-contrast, pixel-perfect Rich CLI with author badges and real-time status.
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
```

---

## 🔒 License & Intellectual Property

**COPYRIGHT (C) 2026 AL HOSSAIN RIFAT. ALL RIGHTS RESERVED.**

This software is strictly proprietary and confidential. No part of this codebase may be copied, modified, redistributed, forked, sublicensed, or used for commercial purposes without explicit, written permission executed directly by the author.

For inquiries, permissions, or custom software architecture:  
🌐 **Portfolio & Contact**: [r1fat.pages.dev](https://r1fat.pages.dev)
