import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1) Excel folder
folder_path = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/VMAT"

# 2) Grab all .xlsx files
excel_files = glob.glob(os.path.join(folder_path, '*.xlsx'))

# 3) Select the sheets to plot (by name)
sheet_names = ['Left Lung EAR', 'Right Lung EAR', 'Total Lungs EAR','Thyroid EAR']

#  Define own titles here
custom_titles = [
    'Ipsilateral Lung',
    'Contralateral Lung',
    'Whole Lung',
    'Thyroid'
]

# Zip them so each sheet_name gets its paired title:
for sheet_name, title in zip(sheet_names, custom_titles):
    # 4) Make a figure with 3 rows × 4 cols
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(20, 15))
    axes_flat = axes.flatten()

    # 5) Loop through each file and plot its data
    for file in excel_files:
        fname = os.path.splitext(os.path.basename(file))[0]
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
        except ValueError:
            idx = sheet_names.index(sheet_name)
            df = pd.read_excel(file, sheet_name=idx)

        x = df.iloc[:, 0].values  # Column A

        age_ticks = np.arange(np.ceil(x.min()/10)*10, x.max()+1, 10)
        for i, col in enumerate(df.columns[1:10]):
            ax = axes_flat[i]
            y = df[col].values

            # Plot and capture the Line2D object to get its color
            line, = ax.plot(x, y, label=fname)
            col_line = line.get_color()

            # Annotate and scatter using the same color
            for age in age_ticks:
                mask = np.isclose(x, age)
                if mask.any():
                    yval = float(y[mask][0])
                    ax.scatter(age, yval, s=20, color=col_line)
                    ax.text(
                        age, yval, f'{yval:.3f}',
                        fontsize=8, va='bottom', ha='center',
                        alpha=0.8, color=col_line
                    )

            ax.set_title(col)

    # 6) Legends
    for ax in axes_flat[:9]:
        ax.legend(fontsize='small')
    # 7) Hide unused axes
    for ax in axes_flat[9:]:
        ax.axis('off')

    # 8) Use your custom title here
    fig.suptitle(title, fontsize=18)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # 9) Save
    out_path = os.path.join(folder_path, f'{title}.png')
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
