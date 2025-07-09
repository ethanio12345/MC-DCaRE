import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Folder containing the Excel files
folder = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/VMAT"

# 1) Gather all real .xlsx files (skip temp "~$" files)
excel_files = [
    os.path.join(folder, f)
    for f in os.listdir(folder)
    if f.lower().endswith(".xlsx") and not f.startswith("~$")
]
if not excel_files:
    raise RuntimeError(f"No .xlsx files found in {folder!r}")

# 2) Read sheet names from the first file
sheet_names = pd.ExcelFile(excel_files[0]).sheet_names

# 3) We want sheets 1–3 → zero-based indices 0,1,2
indices = [0, 1, 2]
regions = [sheet_names[i] for i in indices]
custom_legend_labels = [
    'Ipsilateral Lung (Left)',
    'Contralateral Lung (Right)',
    'Whole Lung (Total)'
]

# 4) Accumulate columns B–J for each region
summary = {r: {j: [] for j in range(1, 10)} for r in regions}
x_axes = {}
for path in excel_files:
    for idx, region in zip(indices, regions):
        df = pd.read_excel(path, sheet_name=idx)
        x_axes.setdefault(region, df.iloc[:, 0].to_numpy())
        for j in range(1, 10):
            summary[region][j].append(df.iloc[:, j].to_numpy())

# 5) Compute means & std devs
avgs = {r: {} for r in regions}
stds = {r: {} for r in regions}
for r in regions:
    for j in range(1, 10):
        arr = np.vstack(summary[r][j])
        avgs[r][j] = arr.mean(axis=0)
        stds[r][j] = arr.std(axis=0)

# 6) Shared y-limits for j=5..9 (if desired)
g2_min, g2_max = np.inf, -np.inf
for j in range(5, 10):
    for r in regions:
        y, s = avgs[r][j], stds[r][j]
        g2_min = min(g2_min, (y - s).min())
        g2_max = max(g2_max, (y + s).max())

# 7) Column labels
sample = pd.read_excel(excel_files[0], sheet_name=indices[0])
col_labels = {j: sample.columns[j] for j in range(1, 10)}

# 8) New 4×1 figure
fig, axes = plt.subplots(4, 1, figsize=(8, 20), sharex=True)
plt.subplots_adjust(hspace=0.4)

# Define which js to combine for each subplot
groups = [
    (1, 2),   # subplot 1: B & C
    (5, 6),   # subplot 2: F & G
    (7, 8),   # subplot 3: H & I
    (9,)      # subplot 4: J only
]

# … everything above is the same …

for ax, js in zip(axes, groups):
    # create a combined title
    title = " & ".join(col_labels[j] for j in js)
    ax.set_title(title, fontweight='bold')
    ax.set_ylabel("EAR (cases per 10,000 PY)", fontweight='bold')

    for region, legend_label in zip(regions, custom_legend_labels):
        x = x_axes[region]

        if len(js) == 2:
            j1, j2 = js
            y1, s1 = avgs[region][j1], stds[region][j1]
            y2, s2 = avgs[region][j2], stds[region][j2]

            line1, = ax.plot(x, y1,
                             linestyle='-',
                             label=f"{legend_label} ({col_labels[j1]})")
            color = line1.get_color()
            ax.fill_between(x, y1 - s1, y1 + s1, alpha=0.2, color=color)

            ax.plot(x, y2,
                    linestyle='--',
                    color=color,
                    label=f"{legend_label} ({col_labels[j2]})")
            ax.fill_between(x, y2 - s2, y2 + s2, alpha=0.2, color=color)

        else:
            j = js[0]
            y, s = avgs[region][j], stds[region][j]
            line, = ax.plot(x, y,
                            linestyle='-',
                            label=f"{legend_label} ({col_labels[j]})")
            color = line.get_color()
            ax.fill_between(x, y - s, y + s, alpha=0.2, color=color)

    # apply shared y-limits if desired
    if any(j >= 5 for j in js):
        ax.set_ylim(g2_min, g2_max)

    # --- NEW: switch y-axis to logarithmic scale ---
    ax.set_yscale('log')

    ax.legend(fontsize='x-small')
    ax.grid(True)

axes[-1].set_xlabel("Age (Yrs)", fontweight='bold')
# … rest of code (saving, showing) unchanged …

# 9) Save and show
out_png = os.path.join(folder, "EARsummaryLungs_combined.png")
fig.savefig(out_png, dpi=300, bbox_inches='tight')
plt.show()

