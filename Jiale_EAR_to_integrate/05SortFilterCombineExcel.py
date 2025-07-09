#!/usr/bin/env python3
import os
import glob
import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────────────────────────
ROOT_DIR      = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT hypo"
KEYWORDS      = ['Lung_L', 'Lung_R', 'Lungs', 'Thyroid']
DESIRED_ORDER = [
    '1cbct','1kvkv','2cbct','2kvkv',
    '1cbct+oof','1kvkv+oof','2cbct+oof','2kvkv+oof',
    'oof'
]

# ─── PROCESS EACH SUB-FOLDER ─────────────────────────────────────────────────
for folder_name in sorted(os.listdir(ROOT_DIR)):
    input_folder = os.path.join(ROOT_DIR, folder_name)
    if not os.path.isdir(input_folder):
        continue  # skip files

    # build output path: same folder, named <folder_name>_combined.xlsx
    output_file = os.path.join(input_folder, f"combined.xlsx")

    # gather CSVs
    csv_map = {
        os.path.splitext(os.path.basename(f))[0]: f
        for f in glob.glob(os.path.join(input_folder, '*.csv'))
    }
    if not csv_map:
        print(f"⚠ No CSVs found in {input_folder!r}, skipping")
        continue

    print(f"→ Combining in '{folder_name}' → '{output_file}'")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet in DESIRED_ORDER:
            path = csv_map.get(sheet)
            if not path:
                print(f"   • Warning: '{sheet}.csv' not found, skipping")
                continue

            df = pd.read_csv(path)
            cols = df.columns.tolist()

            # sort columns by KEYWORDS & type
            target = []
            for kw in KEYWORDS:
                matches = [c for c in cols if kw.lower() in c.lower()]
                matches_sorted = sorted(
                    matches,
                    key=lambda c: (0 if 'dose' in c.lower()
                                   else 1 if 'value' in c.lower()
                                   else 2)
                )
                target += matches_sorted

            target = [c for c in target if c in cols]
            others = [c for c in cols if c not in target]
            df_sorted = df.reindex(columns=target + others) if target else df.copy()

            # drop rows where cols 1,3,5,7 are all zero
            if df_sorted.shape[1] >= 8:
                zero_mask = (
                    (df_sorted.iloc[:, 1] == 0) &
                    (df_sorted.iloc[:, 3] == 0) &
                    (df_sorted.iloc[:, 5] == 0) &
                    (df_sorted.iloc[:, 7] == 0)
                )
                df_sorted = df_sorted.loc[~zero_mask]
            else:
                print(f"   • Sheet '{sheet}' has <8 cols; skipping zero‐filter")

            safe_name = sheet[:31]
            df_sorted.to_excel(writer, sheet_name=safe_name, index=False)
            print(f"   ✔ Wrote '{safe_name}' ({len(df_sorted)} rows)")

    print(f"✅ Saved: {output_file}\n")

