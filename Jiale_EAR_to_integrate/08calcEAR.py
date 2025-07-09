import os
import numpy as np
import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────────────────────────
INPUT_FILE   = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT hypo/CRTH5/CRTH5_combined_divided.xlsx"

# Lung parameters
d_T_lung      = 5.0
fx_lung       = 5
age_x_lung    = 30
gamma_e_lung  = 0.002
gamma_a_lung  = 4.23
R_lung        = 0.83
alpha_lung    = 0.042
beta_lung     = alpha_lung / 3
beta_org_lung = 8.0

# Thyroid parameters
d_T_thy       = 2.667
fx_thy        = 15
age_x_thy     = 30
gamma_e_thy   = -0.046
gamma_a_thy   = 0.6
R_thy         = 0.0
alpha_thy     = 0.0318
beta_thy      = alpha_thy / 3
beta_org_thy  = 0.40

# Age vector
ages = np.arange(30, 81)

# ─── EAR CALCULATORS ──────────────────────────────────────────────────────────
def calculate_ear_lung(V, D, age_a):
    D_T = d_T_lung * fx_lung
    mu = np.exp(gamma_e_lung * (age_x_lung - 30) + gamma_a_lung * np.log(age_a / 70.0))
    alpha_p = alpha_lung + (beta_lung * D / D_T * d_T_lung)
    with np.errstate(over='ignore', invalid='ignore'):
        term1 = (
            1
            - 2 * R_lung
            + R_lung**2 * np.exp(alpha_p * D)
            - (1 - R_lung)**2 * np.exp(-alpha_p * R_lung * D / (1 - R_lung))
        )
        RED = np.exp(-alpha_p * D) / (alpha_p * R_lung) * term1
    OED = np.nansum(V * RED) / np.nansum(V)
    return beta_org_lung * OED * mu

def calculate_ear_thyroid(V, D, age_a):
    D_T = d_T_thy * fx_thy
    mu = np.exp(gamma_e_thy * (age_x_thy - 30) + gamma_a_thy * np.log(age_a / 70.0))
    alpha_p = alpha_thy + (beta_thy * D / D_T * d_T_thy)
    RED = D * np.exp(-alpha_p * D)
    OED = np.sum(V * RED) / np.sum(V)
    return beta_org_thy * OED * mu

# ─── READ SHEETS & COMPUTE ────────────────────────────────────────────────────
xls         = pd.ExcelFile(INPUT_FILE, engine='openpyxl')
sheet_names = xls.sheet_names

ear_L, ear_R, ear_tot, ear_thy = [], [], [], []

for sheet in sheet_names:
    df = pd.read_excel(INPUT_FILE, sheet_name=sheet, usecols="A:H", skiprows=1, engine='openpyxl')
    D_L   = df.iloc[1:, 0].to_numpy();    V_L   = -np.diff(df.iloc[:, 1].to_numpy())
    D_R   = df.iloc[1:, 2].to_numpy();    V_R   = -np.diff(df.iloc[:, 3].to_numpy())
    D_TOT = df.iloc[1:, 4].to_numpy();    V_TOT = -np.diff(df.iloc[:, 5].to_numpy())
    D_THY = df.iloc[1:, 6].to_numpy() if df.shape[1]>=8 else np.array([]); 
    V_THY = -np.diff(df.iloc[:, 7].to_numpy()) if df.shape[1]>=8 else np.array([])

    ear_L  .append([calculate_ear_lung(V_L,   D_L,   a) for a in ages])
    ear_R  .append([calculate_ear_lung(V_R,   D_R,   a) for a in ages])
    ear_tot.append([calculate_ear_lung(V_TOT, D_TOT, a) for a in ages])
    ear_thy.append([calculate_ear_thyroid(V_THY, D_THY, a) if V_THY.size else np.nan for a in ages])

# ─── EXCESS CALCS ─────────────────────────────────────────────────────────────
ex_labels, ex_L, ex_R, ex_tot, ex_thy = [], [], [], [], []

for i in range(0, len(sheet_names), 2):
    if i+1<len(sheet_names):
        label = f"{sheet_names[i]} - {sheet_names[i+1]}"
        ex_labels.append(label)
        ex_L  .append(np.array(ear_L[i])   - np.array(ear_L[i+1]))
        ex_R  .append(np.array(ear_R[i])   - np.array(ear_R[i+1]))
        ex_tot.append(np.array(ear_tot[i]) - np.array(ear_tot[i+1]))
        ex_thy.append(np.array(ear_thy[i]) - np.array(ear_thy[i+1]))

# ─── BUILD DATAFRAMES ─────────────────────────────────────────────────────────
df_L      = pd.DataFrame({sheet_names[i]:   ear_L[i]    for i in range(len(sheet_names))}, index=ages)
df_R      = pd.DataFrame({sheet_names[i]:   ear_R[i]    for i in range(len(sheet_names))}, index=ages)
df_TOT    = pd.DataFrame({sheet_names[i]:   ear_tot[i]  for i in range(len(sheet_names))}, index=ages)
df_THY    = pd.DataFrame({sheet_names[i]:   ear_thy[i]  for i in range(len(sheet_names))}, index=ages)
df_ex_L   = pd.DataFrame({ex_labels[i]:       ex_L[i]   for i in range(len(ex_labels))}, index=ages)
df_ex_R   = pd.DataFrame({ex_labels[i]:       ex_R[i]   for i in range(len(ex_labels))}, index=ages)
df_ex_TOT = pd.DataFrame({ex_labels[i]:       ex_tot[i] for i in range(len(ex_labels))}, index=ages)
df_ex_THY = pd.DataFrame({ex_labels[i]:       ex_thy[i] for i in range(len(ex_labels))}, index=ages)

# ─── BACK IN YOUR ORIGINAL BLOCK: DETERMINE OUTPUT PATH ──────────────────────
parent_folder_name = os.path.basename(os.path.dirname(INPUT_FILE))
output_folder      = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT hypo"
OUTPUT_FILE        = os.path.join(output_folder, parent_folder_name + ".xlsx")

# ─── EXPORT EVERYTHING ─────────────────────────────────────────────────────────
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df_L     .to_excel(writer, sheet_name="Left Lung EAR",      index_label="Age")
    df_R     .to_excel(writer, sheet_name="Right Lung EAR",     index_label="Age")
    df_TOT   .to_excel(writer, sheet_name="Total Lung EAR",     index_label="Age")
    df_THY   .to_excel(writer, sheet_name="Thyroid EAR",        index_label="Age")
    df_ex_L  .to_excel(writer, sheet_name="Left Lung Excess",   index_label="Age")
    df_ex_R  .to_excel(writer, sheet_name="Right Lung Excess",  index_label="Age")
    df_ex_TOT.to_excel(writer, sheet_name="Total Lung Excess",  index_label="Age")
    df_ex_THY.to_excel(writer, sheet_name="Thyroid Excess",     index_label="Age")

print(f"✅ Workbook saved to: {OUTPUT_FILE}")
