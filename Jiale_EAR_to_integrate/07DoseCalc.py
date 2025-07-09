import pandas as pd
import numpy as np
import glob
import os

# This function remains from your previous request, implementing your custom formula
def calculate_user_specified_average_dose(doses_series, volumes_series):
    """
    Calculates a custom average dose based on the user's specific formula:
    1. For each row i: product_i = dose_i * volume_i
    2. sum_of_products = sum(product_i)
    3. sum_of_volumes = sum(volume_i) (where volume_i is the direct value from the volume column)
    4. If sum_of_volumes is 0, result is NaN.
    5. Otherwise, intermediate_result = sum_of_products / sum_of_volumes
    6. Final result = intermediate_result / 15.0

    Args:
        doses_series (pd.Series): Series of dose values.
        volumes_series (pd.Series): Series of corresponding volume values from the input column.

    Returns:
        float: The calculated custom average dose, or np.nan if calculation is not possible.
    """
    # Create a temporary DataFrame to handle potential non-numeric data and NaNs
    temp_df = pd.DataFrame({
        'dose': pd.to_numeric(doses_series, errors='coerce'),
        'volume': pd.to_numeric(volumes_series, errors='coerce')
    }).dropna().reset_index(drop=True) # Drop rows where dose or volume couldn't be converted or were NaN

    # If after cleaning, the DataFrame is empty, no calculation is possible
    if temp_df.empty:
        return np.nan

    doses = temp_df['dose']
    volumes = temp_df['volume']

    # Calculate sum of (dose * volume)
    sum_dose_times_volume = (doses * volumes).sum()
    # Calculate sum of all volumes
    sum_all_volumes = volumes.sum()

    # Avoid division by zero if sum_all_volumes is 0
    if sum_all_volumes == 0:
        return np.nan

    # Calculate intermediate average dose
    intermediate_average_dose = sum_dose_times_volume / sum_all_volumes
    # Calculate final average dose according to the user's formula
    final_average_dose = intermediate_average_dose / 15.0
    return final_average_dose

def process_single_excel_file(file_path):
    """
    Processes a single Excel file. For ALL its sheets,
    it calculates mean doses for DVHs using the user-specified formula.
    It prints the "overall average dose for sheet" for this file and
    returns a dictionary of these averages {sheet_name: overall_avg_dose}.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary of {sheet_name: overall_avg_dose} for the processed file.
              Returns an empty dictionary if the file can't be read or no sheets are processed.
    """
    try:
        # Attempt to read the Excel file
        excel_file = pd.ExcelFile(file_path)
    except Exception as e:
        # Print an error message if the file cannot be read
        print(f"        Error reading Excel file '{os.path.basename(file_path)}': {e}")
        return {}

    summary_sheet_averages_for_this_file = {}
    # Get all sheet names from the Excel file
    sheet_names_to_process = excel_file.sheet_names
    
    if not sheet_names_to_process:
        # If no sheets are found, print a message and return an empty dictionary
        print(f"        No sheets found in '{os.path.basename(file_path)}'.")
        return {}

    file_had_processable_sheets = False
    # Iterate over each sheet in the file
    for sheet_name in sheet_names_to_process:
        print(f"        --- Processing sheet: {sheet_name} ---")
        try:
            # Read the current sheet into a DataFrame, without a header row
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        except Exception as e:
            # If a sheet cannot be read, print an error and skip to the next sheet
            print(f"            Could not read sheet '{sheet_name}'. Error: {e}")
            continue

        # Check if the sheet has at least 6 columns (A-F for 3 DVHs)
        if df.shape[1] < 6:
            print(f"            Sheet '{sheet_name}' has fewer than 6 columns. Expected A-F for 3 DVHs. Skipping.")
            continue
        
        file_had_processable_sheets = True
        # Define column indices for the three DVHs (Dose, Volume pairs)
        # DVH 1: Columns A (0) and B (1)
        # DVH 2: Columns C (2) and D (3)
        # DVH 3: Columns E (4) and F (5)
        dvh_column_indices = [(0, 1), (2, 3), (4, 5)]
        sheet_individual_dvh_means = []

        # Process each DVH pair
        for i, (dose_col_idx, vol_col_idx) in enumerate(dvh_column_indices):
            dvh_label = f"DVH {i+1} (Cols {chr(ord('A')+dose_col_idx)}-{chr(ord('A')+vol_col_idx)})"
            # Check if the required columns exist in the DataFrame
            if dose_col_idx >= df.shape[1] or vol_col_idx >= df.shape[1]:
                print(f"                {dvh_label}: Columns not found. Skipping this DVH.")
                sheet_individual_dvh_means.append(np.nan) # Add NaN if columns are missing
                continue
            
            # Extract dose and volume series
            doses = df[dose_col_idx]
            volumes = df[vol_col_idx]
            
            # Calculate the mean dose using the user-specified formula
            mean_dose_val = calculate_user_specified_average_dose(doses, volumes)
            sheet_individual_dvh_means.append(mean_dose_val)
            
            if not np.isnan(mean_dose_val):
                print(f"                Avg dose for {dvh_label}: {mean_dose_val:.4f}")
            else:
                print(f"                Avg dose for {dvh_label}: Could not be calculated.")
        
        # Calculate the overall average for the current sheet from valid DVH means
        valid_dvh_means_for_sheet = [m for m in sheet_individual_dvh_means if not np.isnan(m)]
        if valid_dvh_means_for_sheet:
            overall_sheet_average = sum(valid_dvh_means_for_sheet) / len(valid_dvh_means_for_sheet)
            print(f"            >>> Overall average dose for sheet '{sheet_name}': {overall_sheet_average:.4f} <<<")
            summary_sheet_averages_for_this_file[sheet_name] = overall_sheet_average
        else:
            print(f"            Could not calculate overall average for sheet '{sheet_name}' (no valid DVH averages).")
        print("        " + "-" * (len(f"--- Processing sheet: {sheet_name} ---") + 8)) # Separator line

    if not file_had_processable_sheets and sheet_names_to_process:
         print(f"        No processable sheets found meeting criteria in '{os.path.basename(file_path)}'.")
    
    return summary_sheet_averages_for_this_file

# --- Main execution ---
if __name__ == "__main__":
    folder_path = r"C:\Users\leele\Desktop\NCCS My Research Project\imaging_dosimetry (dvh export)\2025.05.20\VMAT\VMAT1\New folder" # User's provided path

    # Check if the placeholder path is still being used
    if folder_path == "YOUR_FOLDER_PATH_HERE":
        print("Error: Please update the 'folder_path' variable in the script with the actual path to your folder.")
        exit()

    # Check if the specified folder path exists and is a directory
    if not os.path.isdir(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist or is not a directory.")
        exit()

    print(f"\nSearching for Excel files in folder: {folder_path}")
    print(f"Using user-specified calculation for all DVHs: (sum(dose*volume) / sum(volume)) / 15.0")
    print("Processing ALL sheets in each Excel file.") # Updated message
    print("Displaying results to 4 decimal places.\n")

    # Dictionary to store average doses for each sheet name across all files
    cross_file_sheet_averages_accumulator = {}
    
    # Find all .xlsx and .xls files in the specified folder
    excel_files = glob.glob(os.path.join(folder_path, "*.xlsx")) + \
                  glob.glob(os.path.join(folder_path, "*.xls"))

    if not excel_files:
        print(f"No Excel files (.xlsx or .xls) found in the folder: {folder_path}")
        exit()
    
    print(f"Found {len(excel_files)} Excel file(s) to process.\n")

    # Process each found Excel file
    for file_path in excel_files:
        print(f"--- Processing File: {os.path.basename(file_path)} ---")
        # Get the sheet averages for the current file
        sheet_averages_from_this_file = process_single_excel_file(file_path)
        
        # Accumulate the results if any sheets were processed
        if sheet_averages_from_this_file:
            for sheet_name, avg_dose in sheet_averages_from_this_file.items():
                if not np.isnan(avg_dose): # Only add valid (non-NaN) averages
                    # Append the average dose to the list for that sheet name
                    cross_file_sheet_averages_accumulator.setdefault(sheet_name, []).append(avg_dose)
        print(f"--- Finished Processing File: {os.path.basename(file_path)} ---\n")
    
    # --- Summary Across All Files ---
    print("\n\n======================================================================")
    print("=== Average Dose Across All Files (for common sheet names) ===")
    print("======================================================================")
    print(f"Based on user-specified calculation: (sum(dose*volume) / sum(volume)) / 15.0\n")
    
    if not cross_file_sheet_averages_accumulator:
        print("No sheet data was successfully collected across all processed files to average.")
    else:
        # Sort sheet names alphabetically for consistent output
        sorted_common_sheet_names = sorted(cross_file_sheet_averages_accumulator.keys())
        for sheet_name in sorted_common_sheet_names:
            dose_list = cross_file_sheet_averages_accumulator[sheet_name]
            if dose_list: # Ensure there are doses to average
                average_for_sheet_across_files = sum(dose_list) / len(dose_list)
                print(f"    Average for sheet '{sheet_name}' (from {len(dose_list)} file(s)): {average_for_sheet_across_files:.4f}")
            
    print("\nScript finished.")
