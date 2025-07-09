import os
from pydicom import dcmread

# Set the directory
directory = r"/home/dro/Desktop/jiale/MC-DCaRE_runs/OOForiginal/2025.05.30 test"  # path to DICOM files

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".dcm"):  # Only process DICOM files
        file_path = os.path.join(directory, filename)
        
        # Read the DICOM file
        dcm = dcmread(file_path)
        
        # Apply the scaling factor
        dcm.DoseGridScaling = dcm.DoseGridScaling * 100*  (40.05/40.05) # (from Gy to 1mGy) * (scale to 40Gy) 
        
        # Set a new SeriesDescription (overwrite existing)
        dcm.SeriesDescription = "oof"
        
        
        # Create a new filename with 'scaled' appended to the original name
        new_filename = filename.replace(".dcm", "_scaledOriginalGy.dcm")
        new_file_path = os.path.join(directory, new_filename)
        
        # Save the modified DICOM file
        dcm.save_as(new_file_path)	
