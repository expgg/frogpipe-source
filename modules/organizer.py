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
    Scans raw crawl files, processes and maps them to the teacher's exact 10 datasets,
    preserving 100% of the raw columns (zero data loss), and packages them inside
    Desktop/SEO_<Website_Name>.
    """
    target_folder = custom_output_dir or get_target_seo_folder(target_url)
    os.makedirs(target_folder, exist_ok=True)

    print_step("Normalizing Datasets", f"Packaging 11 Audit Tabs to: {target_folder}", phase=(2, 4))

    # Process all 10 datasets preserving 100% of all data columns
    for key, info in AUDIT_TABS_MAPPING.items():
        src_filename = info.get("raw_source")
        dst_filename = info.get("target_file")
        src_path = os.path.join(raw_crawl_dir, src_filename)
        dst_path = os.path.join(target_folder, dst_filename)

        # Special fallback for Search Console: if empty or missing, fallback to response_codes_all.csv
        if key == "search_console":
            resp_src = os.path.join(raw_crawl_dir, "response_codes_all.csv")
            if (not os.path.isfile(src_path) or get_csv_row_count(src_path) == 0) and os.path.isfile(resp_src):
                src_path = resp_src

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
                                df_in[meta_cols].to_csv(dst_path, index=False, encoding="utf-8-sig")
                        except Exception:
                            pass

        if os.path.isfile(src_path):
            shutil.copyfile(src_path, dst_path)

    # Build summary record for each dataset
    datasets_summary = []
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
