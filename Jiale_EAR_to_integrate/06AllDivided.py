import os
import pandas as pd
import re # Import the regular expressions module

# Specify the input file path.
input_file = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/CRT hypo/CRTH5/combined.xlsx"

# Get the directory of the input file.
input_dir = os.path.dirname(os.path.abspath(input_file))

# Extract the parent folder name.
parent = os.path.basename(input_dir.rstrip(os.sep))

# Extract the base file name and extension.
base_name, ext = os.path.splitext(os.path.basename(input_file))

# Create the output file name with the parent folder prepended and "_divided" appended.
output_file = os.path.join(
    input_dir,
    f"{parent}_{base_name}_divided{ext}"
)

# --- START OF MODIFICATIONS FOR NUMBER EXTRACTION ---
def extract_float_from_string(value):
    """
    Extracts the first floating-point number from a string.
    If the value is already a number, it returns it directly.
    If it's a string, it searches for a number pattern (e.g., 123, 123.45, .56).
    Returns the number as a float, or None if no number is found or input is unsuitable.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Regex to find numbers (integer or decimal, positive or negative)
        # It looks for patterns like: 123, 123.45, .45, -123, -123.45
        match = re.search(r"[-+]?\d*\.?\d+", value)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None # Should not happen if regex is correct
        return None
    return None
# --- END OF MODIFICATIONS FOR NUMBER EXTRACTION ---

# Read all sheets first to get access to the first sheet for VL, VR, VT, and VNH
try:
    all_sheets_for_values = pd.read_excel(input_file, sheet_name=None, header=None)
except FileNotFoundError:
    print(f"Error: The input file was not found at {input_file}")
    exit()
except Exception as e:
    print(f"An error occurred while reading the Excel file: {e}")
    exit()

if not all_sheets_for_values:
    print("Error: No sheets found in the Excel file.")
    exit()

first_sheet_name = list(all_sheets_for_values.keys())[0]
first_sheet_df = all_sheets_for_values[first_sheet_name]

# Initialize default values
VL, VR, VT, VNH = 0.0, 0.0, 0.0, 0.0

try:
    if first_sheet_df.shape[0] < 1:
        print(f"Error: The first sheet '{first_sheet_name}' is empty.")
        exit()

    # Extract VL from Column B (index 1)
    if first_sheet_df.shape[1] > 1:
        raw_val_L = first_sheet_df.iloc[0, 1]
        extracted_L = extract_float_from_string(raw_val_L)
        if extracted_L is not None:
            VL = extracted_L
        else:
            print(f"Warning: Could not extract a valid number for VL from '{raw_val_L}' in sheet '{first_sheet_name}', Col B, Row 1. Using default VL={VL}.")
    else:
        print(f"Warning: Column B (for VL) not found in sheet '{first_sheet_name}'. Using default VL={VL}.")

    # Extract VR from Column D (index 3)
    if first_sheet_df.shape[1] > 3:
        raw_val_R = first_sheet_df.iloc[0, 3]
        extracted_R = extract_float_from_string(raw_val_R)
        if extracted_R is not None:
            VR = extracted_R
        else:
            print(f"Warning: Could not extract a valid number for VR from '{raw_val_R}' in sheet '{first_sheet_name}', Col D, Row 1. Using default VR={VR}.")
    else:
        print(f"Warning: Column D (for VR) not found in sheet '{first_sheet_name}'. Using default VR={VR}.")

    # Extract VT from Column F (index 5)
    if first_sheet_df.shape[1] > 5:
        raw_val_T = first_sheet_df.iloc[0, 5]
        extracted_T = extract_float_from_string(raw_val_T)
        if extracted_T is not None:
            VT = extracted_T
        else:
            print(f"Warning: Could not extract a valid number for VT from '{raw_val_T}' in sheet '{first_sheet_name}', Col F, Row 1. Using default VT={VT}.")
    else:
        print(f"Warning: Column F (for VT) not found in sheet '{first_sheet_name}'. Using default VT={VT}.")

    # Extract VNH from Column H (index 7)
    if first_sheet_df.shape[1] > 7:
        raw_val_NH = first_sheet_df.iloc[0, 7]
        extracted_NH = extract_float_from_string(raw_val_NH)
        if extracted_NH is not None:
            VNH = extracted_NH
        else:
            print(f"Warning: Could not extract a valid number for VNH from '{raw_val_NH}' in sheet '{first_sheet_name}', Col H, Row 1. Using default VNH={VNH}.")
    else:
        print(f"Warning: Column H (for VNH) not found in sheet '{first_sheet_name}'. Using default VNH={VNH}.")

    print(f"Using values from sheet '{first_sheet_name}': VL={VL}, VR={VR}, VT={VT}, VNH={VNH}")

except Exception as e:
    print(f"An unexpected error occurred during value extraction: {e}")
    # It might be better to exit if critical values can't be determined,
    # or proceed with defaults if that's acceptable.
    # For now, we'll proceed with defaults if extraction fails at any point above.
    print("Proceeding with potentially default values for multipliers.")


# Define multipliers based on the extracted values.
multiplierL = VL / 100
multiplierR = VR / 100
multiplierEF = VT / 100
multiplierNH = VNH / 100

# Now, use the already read sheets_dict for processing.
sheets_dict = all_sheets_for_values

# Process each sheet:
for sheet_name, df in sheets_dict.items():
    if df.shape[0] > 1:
        header_row = df.iloc[0]
        data_rows = df.iloc[1:].copy()

        if not data_rows.empty:
            # Process Column A (index 0): Divide by 1000
            if data_rows.shape[1] > 0:
                data_rows.iloc[:, 0] = pd.to_numeric(data_rows.iloc[:, 0], errors='coerce') / 1000

            # Process Column B (index 1): Multiply by multiplierL
            if data_rows.shape[1] > 1:
                data_rows.iloc[:, 1] = pd.to_numeric(data_rows.iloc[:, 1], errors='coerce') * multiplierL

            # Process Column C (index 2): Divide by 1000
            if data_rows.shape[1] > 2:
                data_rows.iloc[:, 2] = pd.to_numeric(data_rows.iloc[:, 2], errors='coerce') / 1000

            # Process Column D (index 3): Multiply by multiplierR
            if data_rows.shape[1] > 3:
                data_rows.iloc[:, 3] = pd.to_numeric(data_rows.iloc[:, 3], errors='coerce') * multiplierR

            # Process Column E (index 4): Divide by 1000
            if data_rows.shape[1] > 4:
                data_rows.iloc[:, 4] = pd.to_numeric(data_rows.iloc[:, 4], errors='coerce') / 1000

            # Process Column F (index 5): Multiply by multiplierEF
            if data_rows.shape[1] > 5:
                data_rows.iloc[:, 5] = pd.to_numeric(data_rows.iloc[:, 5], errors='coerce') * multiplierEF
            
            # Process Column G (index 6): Divide by 1000
            if data_rows.shape[1] > 6:
                data_rows.iloc[:, 6] = pd.to_numeric(data_rows.iloc[:, 6], errors='coerce') / 1000

            # Process Column H (index 7): Multiply by multiplierNH
            if data_rows.shape[1] > 7:
                data_rows.iloc[:, 7] = pd.to_numeric(data_rows.iloc[:, 7], errors='coerce') * multiplierNH

            sheets_dict[sheet_name] = pd.concat(
                [header_row.to_frame().T, data_rows],
                ignore_index=True
            )
        else: 
            sheets_dict[sheet_name] = header_row.to_frame().T
    else:
        sheets_dict[sheet_name] = df

try:
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df_to_write in sheets_dict.items():
            df_to_write.to_excel(writer, sheet_name=sheet_name, header=False, index=False)
    print(f"Processed file saved as: {output_file}")
except Exception as e:
    print(f"An error occurred while writing the output Excel file: {e}")

