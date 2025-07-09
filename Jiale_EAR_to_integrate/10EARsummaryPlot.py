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
xls0 = pd.ExcelFile(excel_files[0])
sheet_names = xls0.sheet_names

# 3) We want sheets 1–3 → zero-based indices 0,1,2
indices = [0, 1, 2]
regions = [sheet_names[i] for i in indices]

# Define custom legend labels here:
custom_legend_labels = [
    'Ipsilateral Lung (Left)',
    'Contralateral Lung (Right)',
    'Whole Lung (Total)'
]
assert len(custom_legend_labels) == len(regions), "Need one label per region"

# 4) Accumulate columns B–J for each region
summary = {r: {j: [] for j in range(1, 10)} for r in regions}
x_axes = {}
for path in excel_files:
    for idx, region in zip(indices, regions):
        df = pd.read_excel(path, sheet_name=idx)
        if region not in x_axes:
            x_axes[region] = df.iloc[:, 0].to_numpy()
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

# 6) Compute shared y-limits for the last 5 plots (cols F–J: j=5..9)
g2_min, g2_max = np.inf, -np.inf
for j in range(5, 10):
    for r in regions:
        y = avgs[r][j]
        s = stds[r][j]
        g2_min = min(g2_min, (y - s).min())
        g2_max = max(g2_max, (y + s).max())

# 7) Get real column labels from the first sheet
sample = pd.read_excel(excel_files[0], sheet_name=indices[0])
col_labels = {j: sample.columns[j] for j in range(1, 10)}

# 8) Create a 3×4 grid of subplots
fig, axes = plt.subplots(3, 4, figsize=(20, 15))
axes_flat = axes.flatten()

# 9) Plot each of the nine (B–J) into axes_flat[0]…axes_flat[8]
for i, j in enumerate(range(1, 10)):
    ax = axes_flat[i]
    ax.set_title(col_labels[j])
    ax.set_xlabel("Age (Yrs)")
    ax.set_ylabel("EAR (cases per 10,000 PY)")

    color_map = {}
    for region, legend_label in zip(regions, custom_legend_labels):
        x = x_axes[region]
        y = avgs[region][j]
        s = stds[region][j]

        line, = ax.plot(x, y, label=legend_label)
        color_map[region] = line.get_color()
        ax.fill_between(x, y - s, y + s, alpha=0.3)

    if i >= 4:
        ax.set_ylim(g2_min, g2_max)

    ages = np.arange(np.ceil(x.min() / 10) * 10, x.max() + 1, 10)
    for age in ages:
        mask = np.isclose(x, age)
        if not mask.any():
            continue
        for region in regions:
            yv = avgs[region][j][mask][0]
            sv = stds[region][j][mask][0]
            col = color_map[region]
            ax.scatter(age, yv, s=20, color=col)
            ax.text(
                age, yv, f"{yv:.3f}±{sv:.3f}",
                fontsize=8, va='bottom', ha='center', alpha=0.8, color=col
            )

    ax.legend(fontsize='small')

# 10) Turn off the extra three axes (bottom row cols 2–4)
for ax in axes_flat[9:]:
    ax.axis('off')

# 11) Adjust spacing
fig.suptitle("Average EAR ± Std Dev", fontsize=22, y=0.94)
fig.tight_layout(rect=[0, 0.05, 1, 0.90])
fig.subplots_adjust(hspace=0.4, wspace=0.3)

# 12) Show & save figure
out_png = os.path.join(folder, "EARsummaryLungs.png")
fig.savefig(out_png, dpi=300)

# # 13) Export mean and std to Excel
# out_excel = os.path.join(folder, "EARsummary_stats.xlsx")
# with pd.ExcelWriter(out_excel) as writer:
#     for region in regions:
#         df_stats = pd.DataFrame({'Age': x_axes[region]})
#         for j in range(1, 10):
#             col = col_labels[j]
#             df_stats[f"{col} Mean"] = avgs[region][j]
#             df_stats[f"{col} Std"] = stds[region][j]
#         sheet_name = region[:31]
#         df_stats.to_excel(writer, sheet_name=sheet_name, index=False)
# print(f"Saved mean & std stats to {out_excel}")
