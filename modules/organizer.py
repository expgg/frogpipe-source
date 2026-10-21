"""
FrogPipe — Audit File Organizer & Dataset Normalizer
Architected by Al Hossain Rifat
"""

import os
import shutil
import json
import csv
import pandas as pd
from typing import Dict, List, Any

from modules.config import AUDIT_TABS_MAPPING, get_target_seo_folder, extract_clean_domain
from modules.ui import print_step, print_success, print_warning


def get_csv_row_count(file_path: str) -> int:
    """Returns number of data rows in a CSV file (excluding header)."""
    if not os.path.isfile(file_path):
        return 0
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = sum(1 for _ in reader)
            return max(0, rows - 1)
    except Exception:
        return 0


def merge_h1_h2(h1_file: str, h2_file: str, output_file: str) -> bool:
    """
    Combines H1 and H2 crawl CSVs on Address into a single unified 2_H1_H2.csv file.
    """
    try:
        h1_df = pd.read_csv(h1_file, low_memory=False) if os.path.isfile(h1_file) else None
        h2_df = pd.read_csv(h2_file, low_memory=False) if os.path.isfile(h2_file) else None

        if h1_df is not None and h2_df is not None:
            # Keep key columns from H1 and H2
            cols_h1 = [c for c in h1_df.columns if c in ["Address", "H1-1", "H1-2", "H1-Length 1", "H1-Length 2", "Status Code", "Indexability"]]
            cols_h2 = [c for c in h2_df.columns if c in ["Address", "H2-1", "H2-2", "H2-Length 1", "H2-Length 2"]]
            
            sub_h1 = h1_df[cols_h1] if cols_h1 else h1_df
            sub_h2 = h2_df[cols_h2] if cols_h2 else h2_df
            
            merged = pd.merge(sub_h1, sub_h2, on="Address", how="outer")
            merged.to_csv(output_file, index=False, encoding="utf-8-sig")
            return True
        elif h1_df is not None:
            h1_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            return True
        elif h2_df is not None:
            h2_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            return True
    except Exception as e:
        # Fallback copy
        if os.path.isfile(h1_file):
            shutil.copyfile(h1_file, output_file)
            return True
    return False


def organize_audit_datasets(
    raw_crawl_dir: str,
    target_url: str,
    custom_output_dir: str = None
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Scans raw crawl files, processes and maps them to the teacher's exact 9 datasets,
    and packages them inside Desktop/SEO_<Website_Name>.
    """
    target_folder = custom_output_dir or get_target_seo_folder(target_url)
    os.makedirs(target_folder, exist_ok=True)

    print_step("Normalizing Datasets", f"Packaging to: {target_folder}")

    # Mapping of raw Screaming Frog files to our 9 target files
    datasets_summary = []

    # 1. Issues
    issues_src = os.path.join(raw_crawl_dir, "issues_overview_report.csv")
    issues_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["issues"]["target_file"])
    if os.path.isfile(issues_src):
        shutil.copyfile(issues_src, issues_dst)

    # 2. H1 + H2
    h1_src = os.path.join(raw_crawl_dir, "h1_all.csv")
    h2_src = os.path.join(raw_crawl_dir, "h2_all.csv")
    h1_h2_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["h1_h2"]["target_file"])
    merge_h1_h2(h1_src, h2_src, h1_h2_dst)

    # 3. Meta Tags & Description
    meta_src = os.path.join(raw_crawl_dir, "meta_description_all.csv")
    meta_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["meta"]["target_file"])
    if os.path.isfile(meta_src):
        shutil.copyfile(meta_src, meta_dst)

    # 4. Content
    content_src = os.path.join(raw_crawl_dir, "content_all.csv")
    content_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["content"]["target_file"])
    if os.path.isfile(content_src):
        shutil.copyfile(content_src, content_dst)

    # 5. ALL Page Titles
    titles_src = os.path.join(raw_crawl_dir, "page_titles_all.csv")
    titles_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["page_titles"]["target_file"])
    if os.path.isfile(titles_src):
        shutil.copyfile(titles_src, titles_dst)

    # 6. URLs
    urls_src = os.path.join(raw_crawl_dir, "internal_all.csv")
    urls_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["urls"]["target_file"])
    if os.path.isfile(urls_src):
        shutil.copyfile(urls_src, urls_dst)

    # 7. Images
    images_src = os.path.join(raw_crawl_dir, "images_all.csv")
    images_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["images"]["target_file"])
    if os.path.isfile(images_src):
        shutil.copyfile(images_src, images_dst)

    # 8. Search Console Status / Response Codes
    gsc_src = os.path.join(raw_crawl_dir, "search_console_all.csv")
    resp_src = os.path.join(raw_crawl_dir, "response_codes_all.csv")
    gsc_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["search_console"]["target_file"])
    
    # If GSC is empty or missing, fallback to Response Codes
    chosen_status_src = gsc_src if (os.path.isfile(gsc_src) and get_csv_row_count(gsc_src) > 0) else resp_src
    if os.path.isfile(chosen_status_src):
        shutil.copyfile(chosen_status_src, gsc_dst)

    # 9. Canonicals
    canon_src = os.path.join(raw_crawl_dir, "canonicals_all.csv")
    canon_dst = os.path.join(target_folder, AUDIT_TABS_MAPPING["canonicals"]["target_file"])
    if os.path.isfile(canon_src):
        shutil.copyfile(canon_src, canon_dst)

    # Build summary record for each dataset
    for key, info in AUDIT_TABS_MAPPING.items():
        dst_path = os.path.join(target_folder, info["target_file"])
        exists = os.path.isfile(dst_path)
        size_kb = (os.path.getsize(dst_path) / 1024.0) if exists else 0.0
        row_count = get_csv_row_count(dst_path) if exists else 0

        datasets_summary.append({
            "key": key,
            "title": info["title"],
            "target_file": info["target_file"],
            "description": info["description"],
            "found": exists,
            "size_kb": size_kb,
            "rows": row_count,
            "full_path": dst_path
        })

    # Write manifest.json
    manifest = {
        "engine": "FrogPipe Mark 1",
        "architect": "Al Hossain Rifat",
        "target_url": target_url,
        "clean_slug": extract_clean_domain(target_url),
        "target_folder": target_folder,
        "datasets": datasets_summary
    }
    with open(os.path.join(target_folder, "audit_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return target_folder, datasets_summary
