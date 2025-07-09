
import os
from pydicom import dcmread

# Set the directory
directory = r"C:\Users\leele\Desktop\NCCS My Research Project\MC-DCaRE_runs\2025.05.15\Hyp CBCT" # Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".dcm"):  # Only process DICOM files
        file_path = os.path.join(directory, filename)
        
        # Read the DICOM file
        dcm = dcmread(file_path)
        
        # Apply the scaling factor
        dcm.DoseGridScaling = dcm.DoseGridScaling * (19756184/2.4) * 1000 * (5) # (2844578000)*(from Gy to 1mGy*15 fraction) factor *cbct>kvkv imaging
        # Set a new SeriesDescription (overwrite existing)
        dcm.SeriesDescription = "1cbct"
        
        # Create a new filename with 'scaled' appended to the original name
        new_filename = filename.replace(".dcm", "_scaled5Fxcbct.dcm")
        new_file_path = os.path.join(directory, new_filename)
        
        # Save the modified DICOM file
        dcm.save_as(new_file_path)


