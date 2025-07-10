import os
import numpy as np
import pydicom
import SimpleITK as sitk
from copy import deepcopy


def scale_dose(directory:str, fractions:int, image_mode:str, plan_dose:float=None, target_plan_dose:float= 40.05):
    '''
    directory is the folder directory with the imaging dose dicom 
    fractions is the number of fractions for this plan, therefore multiples the number of times the patient receive this dose
    image_mode 
    plan_dose is the original plan dose to be scaled up
    target_plan_dose is the dose to scale to, by default scales all plan dose to 40 Gy for comparism
    '''

    for filename in os.listdir(directory):
        if filename.endswith(".dcm"):  # Only process DICOM files
            file_path = os.path.join(directory, filename)
            # Read the DICOM file
            dcm = pydicom.dcmread(file_path)
            scale_factor = 1000  # Change topas dicom file from Gy to mGy 

            if image_mode == "cbct":
                dcm.DoseGridScaling = dcm.DoseGridScaling * (19756184/2.4) * scale_factor * fractions # (2844578000)*(from Gy to 1mGy)*(n fraction)*cbct>kvkv imaging
                # Set a new SeriesDescription (overwrite existing)
                dcm.SeriesDescription = "1cbct" 
                
                # Create a new filename with 'scaled' appended to the original name
                new_filename = filename.replace(".dcm", "_scaled"+str(fractions)+"Fxcbct.dcm")
                new_file_path = os.path.join(directory, new_filename)
                
                # Save the modified DICOM file
                dcm.save_as(new_file_path)
            
            elif image_mode == "kVkV":
                dcm.DoseGridScaling = dcm.DoseGridScaling * (19756184/2.4) * scale_factor * fractions * (2/27) # (2844578000)*(from Gy to 1mGy)*(n fraction)*cbct>kvkv imaging
        
                # Set a new SeriesDescription (overwrite existing)
                dcm.SeriesDescription = "1kvkv"
        
                # Create a new filename with 'scaled' appended to the original name
                new_filename = filename.replace(".dcm", "_scaled"+str(fractions)+"Fx1kvkv.dcm")
                new_file_path = os.path.join(directory, new_filename)
                
                # Save the modified DICOM file
                dcm.save_as(new_file_path)

            elif image_mode == "plan dose":
                # Apply the scaling factor
                dcm.DoseGridScaling = dcm.DoseGridScaling * scale_factor *  (target_plan_dose/plan_dose) # (from Gy to 1mGy) * (scale to 40Gy) 
                # dcm.DoseGridScaling = dcm.DoseGridScaling * 100*  (40.05/25.5) # (from Gy to 1mGy) * (scale to 40Gy) WHY 40.05 AND 25.5

                # Set a new SeriesDescription (overwrite existing)
                dcm.SeriesDescription = "oof"
                
                # Create a new filename with 'scaled' appended to the original name
                new_filename = filename.replace(".dcm", "_scaled" + str(plan_dose) + "to" + str(target_plan_dose) + "Gy.dcm")
                new_file_path = os.path.join(directory, new_filename)
                
                # Save the modified DICOM file
                dcm.save_as(new_file_path)

#######################################################################################################################################################
# def make_uid(): #Depreciated by directly calling the function in the line
#     return pydicom.uid.generate_uid()

def read_rt_dose(path):
    ds = pydicom.dcmread(path)
    if ds.Modality != 'RTDOSE':
        raise ValueError(f"{path} is not an RTDOSE")
    sitk_img = sitk.ReadImage(path)
    arr = sitk.GetArrayFromImage(sitk_img)  # shape = (Z, Y, X)
    scale = float(ds.DoseGridScaling)
    desc = ""
    if hasattr(ds, 'SeriesDescription'): # SeriesDescription is Type 2, so may not exist
        desc = ds.SeriesDescription.lower()
    else:
        print(f"Warning: SeriesDescription missing in {path}. Identification might fail.")
    return ds, sitk_img, arr, scale, desc

def load_doses(folder):
    doses = {}
    print(f"  Loading doses from: {folder}")
    for fn in os.listdir(folder):
        full = os.path.join(folder, fn)
        if os.path.isfile(full) and fn.lower().endswith('.dcm'): # Process only DICOM files
            try:
                ds, img, arr, scale, desc = read_rt_dose(full)
            except ValueError: # Catch specific RTDOSE error
                continue
            except Exception as e:
                print(f"    Could not read or process DICOM file {fn}: {e}")
                continue

            if 'oof' in desc: doses['oof'] = (ds, img, arr, scale)
            elif '1cbct' in desc: doses['1cbct'] = (ds, img, arr, scale)
            elif '1kvkv' in desc: doses['1kvkv'] = (ds, img, arr, scale)
    return doses

def resample_to_ref(img, ref_img_param): # Changed ref_img to ref_img_param to avoid confusion
    if (img.GetSize() == ref_img_param.GetSize() and
            img.GetSpacing() == ref_img_param.GetSpacing() and
            img.GetOrigin() == ref_img_param.GetOrigin() and
            img.GetDirection() == ref_img_param.GetDirection()):
        return img
    rf = sitk.ResampleImageFilter()
    rf.SetReferenceImage(ref_img_param)
    rf.SetInterpolator(sitk.sitkLinear)
    return rf.Execute(img)

# CORRECTED FUNCTION:
def combine_and_save(folder, name, keys, doses):
    # use the first key as reference
    ds_ref, img_ref, arr_ref, scale_ref = doses[keys[0]] # img_ref is defined here
    total_gy = None

    print(f"  Combining for '{name}': {keys}")
    for k in keys:
        if k not in doses:
            print(f"    Error: Dose key '{k}' not found for combination '{name}'. Skipping this combination.")
            return

        ds_k, img_k, arr_k, scale_k = doses[k]

        # Check if img_k needs resampling
        if (img_k.GetSize() != img_ref.GetSize() or
            img_k.GetSpacing() != img_ref.GetSpacing() or # <<< CORRECTED THIS LINE (was ref_img)
            img_k.GetOrigin() != img_ref.GetOrigin() or
            img_k.GetDirection() != img_ref.GetDirection()):
            img_rs = resample_to_ref(img_k, img_ref) # Pass img_ref here
            print(f"    • Resampling {k}: original {arr_k.shape} → resampled {sitk.GetArrayFromImage(img_rs).shape}")
        else:
            img_rs = img_k
            print(f"    • Using {k} (no resampling needed): original {arr_k.shape}")

        arr_rs = sitk.GetArrayFromImage(img_rs)
        gy = arr_rs * scale_k
        total_gy = gy if total_gy is None else total_gy + gy

    if total_gy is None:
        print(f"    Warning: No doses were combined for '{name}'. Skipping save.")
        return

    if scale_ref == 0:
        print(f"    Error: DoseGridScaling for reference dose '{keys[0]}' is zero. Cannot save combined dose '{name}'.")
        return
    out_arr = np.round(total_gy / scale_ref).astype(arr_ref.dtype)

    new = deepcopy(ds_ref)
    new.PixelData = out_arr.tobytes()
    new.Rows, new.Columns = out_arr.shape[1], out_arr.shape[2]
    new.NumberOfFrames = out_arr.shape[0]
    new.SOPInstanceUID = pydicom.uid.generate_uid() # Is this random or built by some unique checksum? If random, the chances of dupli are low but non zero
    new.SeriesInstanceUID = pydicom.uid.generate_uid()
    new.SeriesDescription = name
    new.SpecificCharacterSet = ds_ref.get('SpecificCharacterSet', 'ISO_IR 100')

    if out_arr.dtype == np.uint16:
        new.PixelRepresentation = 0
        new.BitsAllocated = 16
        new.BitsStored = 16
        new.HighBit = 15
    elif out_arr.dtype == np.uint32:
        new.PixelRepresentation = 0
        new.BitsAllocated = 32
        new.BitsStored = 32
        new.HighBit = 31

    new.DoseUnits = ds_ref.get("DoseUnits", "GY")
    new.DoseType = "PHYSICAL"
    new.DoseSummationType = "PLAN" # Adjust as needed
    new.DoseGridScaling = scale_ref

    out_name = f"RTDOSE_{name.replace('+', '_').replace(' ', '_')}.dcm"
    output_path = os.path.join(folder, out_name)
    try:
        new.save_as(output_path)
        print(f"  Saved → {output_path}\n")
    except Exception as e:
        print(f"  Error saving DICOM file {output_path}: {e}\n")

# --- (process_dicom_set and process_all_dicom_sets_in_parent are the same as your previous version) ---
def process_dicom_set(dicom_set_folder):
    print(f"\nProcessing DICOM set in folder: {dicom_set_folder}")
    doses = load_doses(dicom_set_folder)
    required_keys = {'oof', '1cbct', '1kvkv'}
    loaded_keys = set(doses.keys())

    if not required_keys.issubset(loaded_keys):
        missing_keys = required_keys - loaded_keys
        print(f"  Warning: Missing required base dose types in {dicom_set_folder}: {missing_keys}. Some combinations may not be possible.")

    if not doses:
        print(f"  No suitable RTDOSE files found or loaded in {dicom_set_folder}. Skipping combination.")
        return

    combos = {
        '2cbct': ['1cbct', '1cbct'],
        '2kvkv': ['1kvkv', '1kvkv'], 
    }

    for name, keys in combos.items():
        if all(key in doses for key in keys):
            combine_and_save(dicom_set_folder, name, keys, doses)
        else:
            missing_for_combo = [key for key in keys if key not in doses]
            print(f"  Skipping combination '{name}' due to missing dose types: {missing_for_combo}")
    print(f"Finished processing DICOM set: {dicom_set_folder}")


def process_all_dicom_sets_in_parent(parent_folder):
    print(f"Starting processing for parent folder: {parent_folder}")
    if not os.path.isdir(parent_folder):
        print(f"Error: Provided path '{parent_folder}' is not a directory or does not exist.")
        return

    subdirectories = [f.path for f in os.scandir(parent_folder) if f.is_dir()]

    if not subdirectories:
        print(f"No subdirectories found in '{parent_folder}'.")
        print(f"Attempting to process '{parent_folder}' as a single DICOM set.")
        process_dicom_set(parent_folder)
        return

    for subdir in subdirectories:
        try:
            process_dicom_set(subdir)
        except Exception as e:
            print(f"!!! An unexpected error occurred while processing folder {subdir}: {e}")
            import traceback
            traceback.print_exc()
            print(f"--- Skipping to next folder due to error in {subdir} ---")
    print("\nAll DICOM sets processed.")


if __name__ =="__main__":
    directory_list = ["/home/jkgan/Test_dicom_bug_issue/IMDOSE_B5", "/home/jkgan/Test_dicom_bug_issue/LBCRT005","/home/jkgan/Test_dicom_bug_issue/LBVMAT005"] #for testing
    image_mode_list = ["CBCT","kVkV","plan dose"] # for testing
    fractions = 15
    #### Step 1 ####
    # scale_dose(directory_list,fractions[0],image_mode_list[0], plan_dose=25.5, target_plan_dose=40.05)

    #### Step 2 ####
    print(f"Running script with parent folder: {directory_list[0]}")
    process_all_dicom_sets_in_parent(directory_list[0])

    pass
