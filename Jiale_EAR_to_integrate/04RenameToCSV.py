#!/usr/bin/env python3
import os

# 1. Set your top-level directory here:
root_dir = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT hypo"

# 2. Walk through all subdirectories
for dirpath, dirnames, filenames in os.walk(root_dir):
    for file_name in filenames:
        full_path = os.path.join(dirpath, file_name)
        base_name, _ = os.path.splitext(file_name)
        new_file_name = base_name + ".csv"
        new_full_path = os.path.join(dirpath, new_file_name)
        # 3. Only rename if extension differs
        if full_path != new_full_path:
            os.rename(full_path, new_full_path)
            print(f"Renamed '{full_path}' → '{new_full_path}'")
        else:
            print(f"No change for '{full_path}'")

