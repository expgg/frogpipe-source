"""
FrogPipe — Audit File Organizer & Dataset Normalizer
Architected by Al Hossain Rifat
"""

import os
import shutil
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional

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


def organize_audit_datasets(
    raw_crawl_dir: str,
    target_url: str,
    custom_output_dir: str = None,
    crawl_limit: Optional[int] = None
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Scans raw crawl files, processes and maps them to the teacher's exact 11 datasets,
    preserving 100% of the raw columns (zero data loss), and packages them inside
    audited_sites/SEO_<Website_Name>.
    """
    target_folder = custom_output_dir or get_target_seo_folder(target_url)
    os.makedirs(target_folder, exist_ok=True)

    print_step("Normalizing Datasets", f"Packaging 11 Audit Tabs to: {target_folder}", phase=(2, 4))

    # Track adaptive titles (e.g. if Search Console is actually HTTP Response Codes)
    tab_titles_resolved = {}

    # Process all 11 datasets preserving 100% of all data columns
    for key, info in AUDIT_TABS_MAPPING.items():
        src_filename = info.get("raw_source")
        dst_filename = info.get("target_file")
        src_path = os.path.join(raw_crawl_dir, src_filename)
        dst_path = os.path.join(target_folder, dst_filename)
        resolved_title = info["title"]
        synthesized = False

        # Special fallback for Search Console: if empty or missing, fallback to response_codes_all.csv
        if key == "search_console":
            resp_src = os.path.join(raw_crawl_dir, "response_codes_all.csv")
            if (not os.path.isfile(src_path) or get_csv_row_count(src_path) == 0) and os.path.isfile(resp_src):
                src_path = resp_src
                resolved_title = "HTTP Status & Response Codes"

        tab_titles_resolved[key] = resolved_title

        # Special fallback for Meta Tags: if directives_all.csv missing, check internal_all.csv or meta_keywords
        if key == "meta_tags":
            if not os.path.isfile(src_path) or get_csv_row_count(src_path) == 0:
                kw_src = os.path.join(raw_crawl_dir, "meta_keywords_all.csv")
                if os.path.isfile(kw_src) and get_csv_row_count(kw_src) > 0:
                    src_path = kw_src
                else:
                    internal_src = os.path.join(raw_crawl_dir, "internal_all.csv")
                    if os.path.isfile(internal_src):
                        try:
                            df_in = pd.read_csv(internal_src, low_memory=False)
                            meta_cols = [c for c in df_in.columns if any(m in c.lower() for m in ["address", "meta", "robot", "canonical", "indexability"])]
                            if meta_cols:
                                if crawl_limit and crawl_limit > 0:
                                    df_in = df_in.head(crawl_limit)
                                df_in[meta_cols].to_csv(dst_path, index=False, encoding="utf-8-sig")
                                synthesized = True
                        except Exception:
                            pass

        if not synthesized and os.path.isfile(src_path):
            if crawl_limit and crawl_limit > 0 and key != "issues":
                try:
                    df = pd.read_csv(src_path, low_memory=False, nrows=crawl_limit)
                    df.to_csv(dst_path, index=False, encoding="utf-8-sig")
                except Exception:
                    shutil.copyfile(src_path, dst_path)
            else:
                shutil.copyfile(src_path, dst_path)

    # Build summary record for each dataset
    datasets_summary = []
    for key, info in AUDIT_TABS_MAPPING.items():
        dst_path = os.path.join(target_folder, info["target_file"])
        exists = os.path.isfile(dst_path)
        size_kb = (os.path.getsize(dst_path) / 1024.0) if exists else 0.0
        row_count = get_csv_row_count(dst_path) if exists else 0
        current_title = tab_titles_resolved.get(key, info["title"])

        datasets_summary.append({
            "key": key,
            "title": current_title,
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
