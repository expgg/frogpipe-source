# 🐸 FrogPipe — Autonomous SEO Spider & Audit Engine

> **Mark 1: Headless SEO Spider & 9-Data File Organizer**  
> **Architected by Al Hossain Rifat**

---

## ⚡ Overview

**FrogPipe** is an enterprise-grade automated SEO pipeline that connects directly to the **Screaming Frog SEO Spider CLI**, executes headless crawls on target domains or lead lists, and automatically packages, cleans, and structures the essential **9 SEO Audit Datasets**:

1. **Issues Overview** (`issues_overview_report.csv` -> `1_Issues.csv`)
2. **H1 + H2 Headings** (`h1_all.csv` + `h2_all.csv` -> `2_H1_H2.csv`)
3. **Meta Tags & Descriptions** (`meta_description_all.csv` -> `3_Meta_Tags_Description.csv`)
4. **Content & Word Counts** (`content_all.csv` -> `4_Content.csv`)
5. **Page Titles** (`page_titles_all.csv` -> `5_Page_Titles.csv`)
6. **URLs & Response Status** (`internal_all.csv` -> `6_URLs.csv`)
7. **Images & Alt Attributes** (`images_all.csv` -> `7_Images.csv`)
8. **Search Console / Status Codes** (`search_console_all.csv` / `response_codes_all.csv` -> `8_Search_Console_Status.csv`)
9. **Canonicals** (`canonicals_all.csv` -> `9_Canonicals.csv`)

Automated packaging generates a clean directory directly on the user's Desktop:
`Desktop/SEO_<Website_Domain>/`

---

## 🚀 Features (Mark 1)

- 🐸 **Autonomous Headless Crawling**: Directly taps into `ScreamingFrogSEOSpiderCli.exe`.
- 📁 **Automated Desktop Packaging**: Dynamically resolves domain names and builds clean `SEO_<Domain>` bundles.
- 🧹 **Intelligent Data Normalization**: Extracts, validates, and normalizes raw crawl dumps into standardized audit CSVs.
- 🎨 **Executive Rich CLI**: Cyberpunk emerald terminal UI featuring branded ASCII art, live progress indicators, file size metrics, and clickable local folder paths.
- ⚙️ **Fault-Tolerant Path Detection**: Auto-detects custom Screaming Frog paths (`X:\APPS\Screaming Frog SEO Spider` and default Program Files).

---

## 🛠️ Installation

```bash
git clone https://github.com/expgg/frogpipe-source.git
cd frogpipe-source
pip install -r requirements.txt
```

---

## 💻 Usage

Run the interactive terminal:
```bash
python frogpipe.py
```

Or pass target domains directly via CLI:
```bash
python frogpipe.py --url https://example.com
```

---

## 👤 Author

**Al Hossain Rifat**  
*Lead Automation Architect*
