import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ─── FUNCTIONS ─────────────────────────────────────────────────────────────────

def load_folder_data(folder_path, sheet_name):
    """
    Read all .xlsx files in folder_path, load `sheet_name`,
    return two lists (length=4) of lists of arrays:
      dose_data[i] = [dose_array_file1, dose_array_file2, …] (in Gy)
      vol_data[i]  = [vol_array_file1,  vol_array_file2,  …]
    """
    files = sorted(glob.glob(os.path.join(folder_path, "*.xlsx")))
    if not files:
        raise RuntimeError(f"No .xlsx files found in {folder_path!r}")

    dose_data = [[] for _ in range(4)]
    vol_data  = [[] for _ in range(4)]

    for file in files:
        df = pd.read_excel(file, sheet_name=sheet_name)
        if df.shape[1] < 8:
            raise RuntimeError(f"{file!r} has fewer than 8 columns")

        for i in range(4):
            # dose originally in mGy; convert to Gy
            dose_mGy = df.iloc[:, 2*i].to_numpy()
            dose = dose_mGy / 1000.0
            vol  = df.iloc[:, 2*i+1].to_numpy()
            dose_data[i].append(dose)
            vol_data[i].append(vol)

    return dose_data, vol_data


def plot_summary_no_interp(folder_loads, labels, subplot_titles, figure_title,
                            save_path=None, xlim=None):
    """
    Plot a 2×2 grid of mean±1σ DVHs, padding shorter DVHs to the
    longest dose-array per subplot (same bin width assumed).

    folder_loads:    list of (dose_data, vol_data) tuples
    labels:          legend labels for each folder
    subplot_titles:  list of 4 titles for each subplot
    figure_title:    super-title for the entire figure
    save_path:       full file path to save the figure (optional)
    xlim:            tuple (xmin, xmax) to set x-axis limits (optional)
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    # Bold figure title
    fig.suptitle(figure_title, fontsize=16, fontweight='bold')

    for idx, ax in enumerate(axes):
        for (dose_data, vol_data), label in zip(folder_loads, labels):
            lengths = [len(d) for d in dose_data[idx]]
            ref_idx = int(np.argmax(lengths))
            grid    = dose_data[idx][ref_idx]
            padded_vols = []

            for d_arr, v_arr in zip(dose_data[idx], vol_data[idx]):
                if len(v_arr) < len(grid):
                    pad_size = len(grid) - len(v_arr)
                    v_arr = np.concatenate([v_arr, np.zeros(pad_size)])
                else:
                    v_arr = v_arr[:len(grid)]
                padded_vols.append(v_arr)

            arr  = np.vstack(padded_vols)
            mean = arr.mean(axis=0)
            std  = arr.std(axis=0)

            # Thinner plot lines (linewidth=0.8)
            ax.plot(grid, mean, label=f"{label}", linewidth=0.8)
            ax.fill_between(grid, mean - std, mean + std, alpha=0.3)

        # Bold axis labels
        ax.set_title(subplot_titles[idx], fontweight='bold')
        ax.set_xlabel("Dose (Gy)", fontweight='bold')
        ax.set_ylabel("Volume (%)", fontweight='bold')
        if xlim is not None:
            ax.set_xlim(xlim)
        ax.legend()
        ax.grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # leave space for suptitle

    # Save if requested
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300)
        print(f"Figure saved to: {save_path}")

    plt.show()


# ─── CONFIG ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    folder_paths = [
        r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/VMAT/vmat dvh",
        r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT/crt dvh"
    ]
    labels         = ["VMAT", "3D CRT"]
    sheet_name     = "1cbct"
    subplot_titles = [
        "Ipsilateral Lung", "Contralateral Lung", "Total Lungs", "Thyroid"
    ]  # change to your desired ROI names
    figure_title   = "CBCT Imaging DVH"
    save_folder    = r"/home/dro/Desktop/jiale/Final plots"
    save_filename  = "CBCT_Imaging_DVH2.png"
    save_path      = os.path.join(save_folder, save_filename)
    xlim           = (-0.1, 1.1)  # set your desired x-axis limits (Gy), or None

    # load data for both folders
    folder_loads = [load_folder_data(fp, sheet_name) for fp in folder_paths]

    # plot and save figure with optional x-axis limits
    plot_summary_no_interp(folder_loads, labels, subplot_titles,
                           figure_title, save_path, xlim)

