import os
import pydicom
from pydicom.errors import InvalidDicomError
from dicompylercore import dicomparser, dvhcalc
import pandas as pd
import logging
from collections import defaultdict
import re

# Configure logging to show info level messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_custom_sort_priority(sheet_name_key_original):
    """
    Assigns a sort priority to a sheet name based on a predefined custom order.
    Lower numbers indicate earlier placement. Unmatched names get a higher priority
    and are sorted alphabetically among themselves.
    """
    key = sheet_name_key_original.lower().replace(" ", "").replace("_", "").replace("+","")

    # Desired order: 1cbct, 1kvkv, 2cbct, 2kvkv, 1cbct+oof, 1kvkv+oof, 2cbct+oof, 2kvkv+oof, oof
    # Priority mapping (lower means earlier in sort):
    # 0: 1cbct
    # 1: 1kvkv
    # 2: 2cbct
    # 3: 2kvkv
    # 4: 1cbct+oof
    # 5: 1kvkv+oof
    # 6: 2cbct+oof
    # 7: 2kvkv+oof
    # 8: oof
    # 9: Others (will be sub-sorted alphabetically)

    # Check for most specific combinations first (those with "+oof")
    if "1" in key and "cbct" in key and "oof" in key: return (4, sheet_name_key_original) # 1cbct+oof
    if "1" in key and "kvkv" in key and "oof" in key: return (5, sheet_name_key_original) # 1kvkv+oof
    if "2" in key and "cbct" in key and "oof" in key: return (6, sheet_name_key_original) # 2cbct+oof
    if "2" in key and "kvkv" in key and "oof" in key: return (7, sheet_name_key_original) # 2kvkv+oof

    # Basic combinations (without oof)
    if "1" in key and "cbct" in key: return (0, sheet_name_key_original) # 1cbct
    if "1" in key and "kvkv" in key: return (1, sheet_name_key_original) # 1kvkv
    if "2" in key and "cbct" in key: return (2, sheet_name_key_original) # 2cbct
    if "2" in key and "kvkv" in key: return (3, sheet_name_key_original) # 2kvkv
    
    # Standalone "oof"
    if "oof" in key: return (8, sheet_name_key_original) # oof
    
    # Fallback for any other sheet names
    return (9, sheet_name_key_original)


def sanitize_general_filename(name):
    """Sanitizes a string to be a valid filename component by removing problematic characters."""
    name = str(name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '_', name)
    name = name.strip()
    if not name:
        name = "Unnamed"
    return name

def sanitize_sheet_name(name):
    """Sanitizes a string to be a valid Excel sheet name."""
    if not name:
        name = "Unnamed_Sheet"
    name = str(name)
    name = re.sub(r'[\\/*?:\[\]]', '_', name)
    return name[:31]

def get_dicom_file_info(filepath):
    """Reads DICOM file and extracts relevant information."""
    filename = os.path.basename(filepath)
    try:
        ds = pydicom.dcmread(filepath, stop_before_pixels=True)
        
        sop_class_uid = ds.SOPClassUID
        sop_instance_uid = ds.SOPInstanceUID
        patient_id = ds.get('PatientID', 'UnknownPatientID')
        study_instance_uid = ds.get('StudyInstanceUID', 'UnknownStudyUID')
        series_instance_uid = ds.get('SeriesInstanceUID', 'UnknownSeriesUID')
        modality = ds.get('Modality', 'UNKNOWN')
        series_description = ds.get('SeriesDescription', '')

        frame_of_reference_uid = None
        if 'FrameOfReferenceUID' in ds:
            frame_of_reference_uid = ds.FrameOfReferenceUID
        elif 'ReferencedFrameOfReferenceSequence' in ds and \
             len(ds.ReferencedFrameOfReferenceSequence) > 0 and \
             'FrameOfReferenceUID' in ds.ReferencedFrameOfReferenceSequence[0]:
            frame_of_reference_uid = ds.ReferencedFrameOfReferenceSequence[0].get('FrameOfReferenceUID')
        
        if modality == 'CT' and 'FrameOfReferenceUID' in ds and frame_of_reference_uid is None: 
            frame_of_reference_uid = ds.FrameOfReferenceUID

        referenced_rtplan_uid_from_dose = None
        rtplan_sop_instance_uid_from_plan = None
        file_type = 'UNKNOWN'

        if sop_class_uid == pydicom.uid.RTStructureSetStorage:
            file_type = 'RTSTRUCT'
        elif sop_class_uid == pydicom.uid.RTDoseStorage:
            file_type = 'RTDOSE'
            if 'ReferencedRTPlanSequence' in ds and len(ds.ReferencedRTPlanSequence) > 0:
                if 'ReferencedSOPInstanceUID' in ds.ReferencedRTPlanSequence[0]:
                    referenced_rtplan_uid_from_dose = ds.ReferencedRTPlanSequence[0].get('ReferencedSOPInstanceUID')
        elif sop_class_uid == pydicom.uid.RTPlanStorage:
            file_type = 'RTPLAN'
            rtplan_sop_instance_uid_from_plan = sop_instance_uid
        elif sop_class_uid == pydicom.uid.CTImageStorage:
            file_type = 'CT'
        elif modality in ['RTSTRUCT', 'RTDOSE', 'RTPLAN', 'CT']: 
            file_type = modality
        
        return (file_type, sop_instance_uid, patient_id, study_instance_uid,
                series_instance_uid, frame_of_reference_uid,
                referenced_rtplan_uid_from_dose, rtplan_sop_instance_uid_from_plan,
                filename, series_description)

    except InvalidDicomError:
        logging.debug(f"Invalid DICOM file skipped: {filepath}")
        return 'INVALID', None, None, None, None, None, None, None, filename, None
    except Exception as e:
        logging.warning(f"Error reading DICOM file {filepath}: {e}")
        return 'ERROR', None, None, None, None, None, None, None, filename, None

def find_and_organize_dicom_files(folder_path):
    """Walks through folder, identifies and organizes DICOM files, keyed by PatientID."""
    dicom_files_by_patient = defaultdict(lambda: defaultdict(list))
    logging.info(f"Scanning folder for DICOM files: {folder_path}")
    file_count = 0
    dicom_count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_count += 1
            filepath = os.path.join(root, file)
            if file.lower() == "dicomdir":
                logging.debug(f"Skipping DICOMDIR file: {filepath}")
                continue
            if "." in file.lower() and not file.lower().endswith('.dcm'):
                continue

            (file_type, sop_uid, pat_id, study_uid, series_uid,
             for_uid, ref_plan_uid_from_dose, plan_sop_uid_from_plan,
             filename, series_desc) = get_dicom_file_info(filepath)
            
            if file_type not in ['INVALID', 'ERROR', 'UNKNOWN']:
                dicom_count +=1
                data = {
                    'path': filepath,
                    'sop_instance_uid': sop_uid,
                    'study_instance_uid': study_uid,
                    'series_instance_uid': series_uid,
                    'frame_of_reference_uid': for_uid,
                    'filename': filename,
                    'series_description': series_desc if series_desc else ""
                }
                if file_type == 'RTDOSE':
                    data['referenced_rtplan_uid'] = ref_plan_uid_from_dose
                elif file_type == 'RTPLAN':
                    data['rtplan_sop_instance_uid'] = plan_sop_uid_from_plan
                
                dicom_files_by_patient[pat_id][file_type.lower() + 's'].append(data)

    logging.info(f"Scanned {file_count} files. Found {dicom_count} processable DICOM files.")
    if not dicom_files_by_patient:
        logging.warning("No DICOM files were successfully parsed and organized by patient.")
    return dicom_files_by_patient

def discover_available_rois(organized_files_for_patient):
    """Scans RTSTRUCTs for a specific patient to find unique ROI names."""
    all_roi_names = set()
    logging.info("Discovering available ROIs for current patient...")

    rtstruct_files = organized_files_for_patient.get('rtstructs', [])
    for rs_info in rtstruct_files:
        rs_path = rs_info['path']
        try:
            rtss_parser = dicomparser.DicomParser(rs_path)
            structures = rtss_parser.GetStructures() 
            for _, structure_info in structures.items():
                all_roi_names.add(structure_info['name'])
        except Exception as e:
            logging.warning(f"Could not parse ROIs from {rs_info['filename']} for discovery: {e}")
    
    sorted_rois = sorted(list(all_roi_names)) 
    if sorted_rois:
        logging.info(f"Discovered {len(sorted_rois)} unique ROI names for this patient.")
    else:
        logging.warning("No ROI names were discovered for this patient. Check if RTSTRUCT files are present and readable.")
    return sorted_rois

def get_user_roi_selection(available_rois, patient_id_for_prompt):
    """
    Presents a list of available ROIs to the user for a given patient and gets their selection.
    Returns a list of selected ROI names in the order of user selection.
    If 'all' is chosen, returns a list of all available ROIs in their displayed (alphabetical) order.
    Returns None if the user chooses to 'skip' the patient.
    """
    if not available_rois:
        print(f"No ROIs available for selection for patient {patient_id_for_prompt}.")
        return [] 

    print(f"\n--- ROI Selection for Patient: {patient_id_for_prompt} ---")
    print("Available ROIs:")
    for i, name in enumerate(available_rois):
        print(f"  {i+1}. {name}")
    
    while True:
        try:
            user_input = input(f"Enter ROI numbers for patient {patient_id_for_prompt} in desired order (e.g., 2,1,4), "
                               f"'all' for all listed (in displayed order), or 'skip' for this patient: ").strip().lower()
            if user_input == 'skip':
                print(f"ROI selection skipped for patient {patient_id_for_prompt}.")
                return None 
            if user_input == 'all':
                print(f"All {len(available_rois)} discovered ROIs for patient {patient_id_for_prompt} will be processed in the displayed order.")
                return available_rois[:] 

            selected_indices_in_order = []
            parts = user_input.split(',')
            if not user_input.strip() and not parts : 
                print("No selection made. Please enter ROI numbers, 'all', or 'skip'.")
                continue

            for part in parts:
                part = part.strip()
                if not part: continue 
                index = int(part) - 1 
                if 0 <= index < len(available_rois):
                    selected_indices_in_order.append(index)
                else:
                    raise ValueError(f"ROI number {index+1} is out of range (1-{len(available_rois)}).")
            
            if not selected_indices_in_order and user_input: 
                print("No valid ROI numbers entered. Please try again.")
                continue
            elif not selected_indices_in_order and not user_input: 
                print("No selection made. Please enter ROI numbers, 'all', or 'skip'.")
                continue

            selected_roi_names_in_order = [available_rois[i] for i in selected_indices_in_order]
            print(f"Selected ROIs for patient {patient_id_for_prompt} (in this order): {', '.join(selected_roi_names_in_order)}")
            return selected_roi_names_in_order
        except ValueError as e:
            print(f"Invalid input: {e}. Please use numbers from the list, 'all', or 'skip'.")
        except Exception as e: 
            print(f"An unexpected error occurred during input processing: {e}")


def run_dvh_export_process(all_organized_files_by_patient, output_dir):
    """
    Main process for DVH export: iterates per patient, gets ROI selection,
    calculates DVHs (dividing dose by 100 from previous version for correct Gy), 
    and writes to patient-specific Excel files,
    ordering ROIs as selected and sorting sheets by custom priority.
    """
    if not all_organized_files_by_patient:
        logging.warning("No DICOM data organized by patient. Cannot proceed with DVH export.")
        return

    for patient_id, file_collections_for_patient in all_organized_files_by_patient.items():
        sanitized_patient_id_for_filename = sanitize_general_filename(patient_id)
        logging.info(f"\nProcessing data for Patient ID: {patient_id} (Excel Filename: {sanitized_patient_id_for_filename}.xlsx)")

        available_rois_for_patient = discover_available_rois(file_collections_for_patient)
                
        user_selected_rois_in_order = get_user_roi_selection(available_rois_for_patient, patient_id)
        
        if user_selected_rois_in_order is None: 
            logging.info(f"Skipping patient {patient_id} as per user selection during ROI prompt.")
            continue
        if not user_selected_rois_in_order : 
            logging.warning(f"No ROIs were selected or available for patient {patient_id}. Skipping DVH calculations for this patient.")
            continue

        dvh_data_for_this_patient_excel = defaultdict(lambda: defaultdict(list))
        
        rtstruct_files = file_collections_for_patient.get('rtstructs', [])
        rtdose_files = file_collections_for_patient.get('rtdoses', [])

        if not rtstruct_files:
            logging.warning(f"  No RTSTRUCT files found for Patient {patient_id}. No DVHs will be calculated for this patient.")
            continue
        if not rtdose_files:
            logging.warning(f"  No RTDOSE files found for Patient {patient_id}. No DVHs will be calculated for this patient.")
            continue

        for rs_info in rtstruct_files:
            rs_path = rs_info['path']
            rs_for_uid = rs_info['frame_of_reference_uid']
            
            if not rs_for_uid:
                logging.warning(f"  RTSTRUCT {rs_info['filename']} is missing FrameOfReferenceUID. Cannot be used.")
                continue 
            
            logging.info(f"  Using RTSTRUCT: {rs_info['filename']} (FOR_UID: {rs_for_uid})")
            
            try:
                rtss_parser = dicomparser.DicomParser(rs_path)
                structures_from_dicom = rtss_parser.GetStructures() 
                if not structures_from_dicom:
                    logging.warning(f"  No structures found or parsed in RTSTRUCT: {rs_info['filename']}.")
                    continue
            except Exception as e:
                logging.error(f"    Failed to parse RTSTRUCT {rs_info['filename']}: {e}. Skipping this RTSTRUCT.")
                continue 

            for rd_info in rtdose_files:
                rd_path = rd_info['path']
                rd_for_uid = rd_info['frame_of_reference_uid']
                rd_filename = rd_info['filename']
                rd_series_desc = rd_info.get('series_description', '')

                sheet_name_base = rd_series_desc if rd_series_desc else rd_filename.replace('.dcm','')
                if not sheet_name_base: 
                    sheet_name_base = rd_info.get('sop_instance_uid', 'UnknownDose')
                
                if not rd_for_uid:
                    logging.warning(f"    RTDOSE {rd_filename} is missing FrameOfReferenceUID. Skipping.")
                    continue

                if rs_for_uid != rd_for_uid:
                    logging.debug(f"    Skipping RTDOSE {rd_filename} (FOR_UID mismatch with current RTSTRUCT {rs_info['filename']}).")
                    continue
                
                logging.info(f"    Processing RTDOSE: {rd_filename} (SeriesDesc for sheet key: '{sheet_name_base}')")

                for _, structure_info in structures_from_dicom.items():
                    roi_id_from_dicom = structure_info['id'] 
                    roi_name_from_dicom = structure_info['name']
                    
                    if roi_name_from_dicom not in user_selected_rois_in_order:
                        continue 
                    
                    logging.debug(f"      Calculating DVH for ROI: '{roi_name_from_dicom}' (ID: {roi_id_from_dicom})")
                    
                    try:
                        # Assuming dvhcalc.get_dvh returns dose in Gy by default from dicompyler-core
                        dvh_obj = dvhcalc.get_dvh(rs_path, rd_path, roi_id_from_dicom)
                        if dvh_obj.volume is None or dvh_obj.volume == 0 or not dvh_obj.bincenters.any():
                            logging.warning(f"        ROI '{roi_name_from_dicom}' in {rs_info['filename']} has zero/undefined volume or no dose overlap with {rd_filename}. No DVH points recorded.")
                            continue 
                        
                        dvh_points_for_roi = []
                        for i in range(len(dvh_obj.bincenters)):
                            dvh_points_for_roi.append({
                                'Dose_Gy': round(dvh_obj.bincenters[i], 6), # Assuming bincenters are already in Gy
                                'CumulativeVolume_cm3': round(dvh_obj.counts[i], 6)
                            })
                        
                        dvh_data_for_this_patient_excel[sheet_name_base][roi_name_from_dicom].extend(dvh_points_for_roi)
                        logging.debug(f"        Successfully processed DVH for ROI: '{roi_name_from_dicom}' with RTDOSE {rd_filename}")

                    except Exception as e:
                        logging.error(f"        Could not calculate DVH for ROI '{roi_name_from_dicom}' with RTDOSE {rd_filename}. Reason: {e}")
        
        if not dvh_data_for_this_patient_excel:
            logging.warning(f"No DVH data generated for Patient ID: {patient_id}. No Excel file will be created for this patient.")
            continue

        excel_path_for_patient = os.path.join(output_dir, f"{sanitized_patient_id_for_filename}.xlsx")
        logging.info(f"Attempting to write DVH data for Patient ID: {patient_id} to Excel: {excel_path_for_patient}")
        
        sorted_sheet_base_name_keys = sorted(
            dvh_data_for_this_patient_excel.keys(),
            key=get_custom_sort_priority 
        )

        try:
            with pd.ExcelWriter(excel_path_for_patient, engine='openpyxl') as writer:
                actual_sheet_names_used_count = defaultdict(int) 

                for sheet_base_name_key in sorted_sheet_base_name_keys: 
                    rois_data_for_sheet = dvh_data_for_this_patient_excel[sheet_base_name_key]
                    if not rois_data_for_sheet:
                        continue

                    sheet_data_dict_for_df = {} 
                    max_len = 0 
                    
                    rois_to_write_in_order_for_this_sheet = [
                        roi_name for roi_name in user_selected_rois_in_order
                        if roi_name in rois_data_for_sheet 
                    ]

                    if not rois_to_write_in_order_for_this_sheet:
                        logging.warning(f"No selected ROIs have data for sheet based on '{sheet_base_name_key}'. Skipping this sheet.")
                        continue

                    for roi_name_iter in rois_to_write_in_order_for_this_sheet:
                        dvh_points_list = rois_data_for_sheet.get(roi_name_iter, [])
                        max_len = max(max_len, len(dvh_points_list))

                    for roi_name_iter in rois_to_write_in_order_for_this_sheet:
                        dvh_points_list = rois_data_for_sheet.get(roi_name_iter, [])
                        doses = [p['Dose_Gy'] for p in dvh_points_list] 
                        volumes = [p['CumulativeVolume_cm3'] for p in dvh_points_list]
                        
                        doses.extend([pd.NA] * (max_len - len(doses))) 
                        volumes.extend([pd.NA] * (max_len - len(volumes)))

                        sheet_data_dict_for_df[(roi_name_iter, 'Dose_Gy')] = doses 
                        sheet_data_dict_for_df[(roi_name_iter, 'CumulativeVolume_cm3')] = volumes

                    if not sheet_data_dict_for_df:
                        logging.warning(f"No data columns to write for sheet based on key '{sheet_base_name_key}' for patient {patient_id}.")
                        continue
                        
                    sheet_df_with_multiindex = pd.DataFrame(sheet_data_dict_for_df)
                    
                    ordered_multi_index_tuples = []
                    for roi_name_val in rois_to_write_in_order_for_this_sheet:
                        ordered_multi_index_tuples.append((roi_name_val, 'Dose_Gy')) 
                        ordered_multi_index_tuples.append((roi_name_val, 'CumulativeVolume_cm3'))
                    
                    if ordered_multi_index_tuples:
                        try:
                            existing_cols = sheet_df_with_multiindex.columns
                            valid_ordered_tuples = [t for t in ordered_multi_index_tuples if t in existing_cols]
                            if valid_ordered_tuples:
                                sheet_df_with_multiindex = sheet_df_with_multiindex[pd.MultiIndex.from_tuples(valid_ordered_tuples)]
                            else:
                                logging.warning(f"No valid columns for reordering sheet '{sheet_base_name_key}'. Using default column order.")

                        except KeyError as e:
                            logging.error(f"KeyError during column reordering for sheet '{sheet_base_name_key}': {e}. Proceeding with available columns.")
                            pass


                    sanitized_base_name = sanitize_sheet_name(sheet_base_name_key)
                    count = actual_sheet_names_used_count[sanitized_base_name]
                    actual_sheet_names_used_count[sanitized_base_name] = count + 1
                    
                    final_sheet_name_for_excel = sanitized_base_name
                    if count > 0: 
                        suffix = f"_{count}"
                        if len(sanitized_base_name) + len(suffix) > 31:
                            final_sheet_name_for_excel = sanitized_base_name[:31-len(suffix)] + suffix
                        else:
                            final_sheet_name_for_excel = sanitized_base_name + suffix
                    
                    final_sheet_name_for_excel = sanitize_sheet_name(final_sheet_name_for_excel) 

                    output_data_as_list_of_lists = []
                    for i in range(sheet_df_with_multiindex.columns.nlevels):
                        output_data_as_list_of_lists.append(list(sheet_df_with_multiindex.columns.get_level_values(i)))
                    
                    for record_tuple in sheet_df_with_multiindex.itertuples(index=False, name=None):
                        output_data_as_list_of_lists.append(
                            ['' if pd.isna(x) else x for x in record_tuple] 
                        )
                        
                    final_df_to_write_to_excel = pd.DataFrame(output_data_as_list_of_lists)

                    logging.info(f"  Writing sheet: '{final_sheet_name_for_excel}' (orig key: '{sheet_base_name_key}')")
                    final_df_to_write_to_excel.to_excel(writer, sheet_name=final_sheet_name_for_excel, index=False, header=False)
                
            logging.info(f"Successfully exported DVH data for Patient ID: {patient_id} to {excel_path_for_patient}")

        except Exception as e:
            logging.error(f"An unexpected error occurred while writing Excel file for Patient ID {patient_id}: {e}")
            import traceback
            logging.error(traceback.format_exc())


if __name__ == '__main__':
    # Prompt user for the DICOM input folder
    dicom_input_folder = ""
    output_export_directory = "" # Initialize output directory

    while True:
        dicom_input_folder_temp = input("Please enter the full path to your DICOM input folder: ").strip()
        if os.path.isdir(dicom_input_folder_temp):
            dicom_input_folder = dicom_input_folder_temp # Assign to the main variable only if valid
            break
        else:
            print(f"Error: The path '{dicom_input_folder_temp}' is not a valid directory. Please try again.")

    # --- Determine Output Export Directory ---
    # Set output_export_directory to the parent of the dicom_input_folder
    if dicom_input_folder: 
        # Get the absolute path to resolve any relative paths (e.g., ".")
        abs_input_folder = os.path.abspath(dicom_input_folder)
        output_export_directory = os.path.dirname(abs_input_folder)
        
        # Check if the input was a root directory, in which case dirname might be the root itself.
        # Or if the input was something like "." or ".." that resolves to a path whose parent is itself or unexpected.
        if output_export_directory == abs_input_folder:
            logging.warning(f"Input folder '{abs_input_folder}' is a root directory or its parent resolves to itself. "
                            f"Output will be placed in the input folder itself.")
            output_export_directory = abs_input_folder # Default to input folder itself
        elif not output_export_directory: # Should not happen if abs_input_folder is valid
             logging.error(f"Could not determine a valid parent directory for '{abs_input_folder}'. "
                           f"Defaulting output to the input folder itself.")
             output_export_directory = abs_input_folder

    else:
        logging.error("DICOM input folder was not set. Cannot determine output directory. Exiting.")
        exit(1)
    # -------------------------------------

    # Ensure the output directory exists or create it
    if not os.path.isdir(output_export_directory):
        try:
            os.makedirs(output_export_directory, exist_ok=True)
            logging.info(f"Output directory created: {output_export_directory}")
        except OSError as e:
            logging.error(f"Could not create output directory {output_export_directory}: {e}")
            exit(1) 
            
    print(f"Starting DVH export process...")
    print(f"Input DICOM folder: {dicom_input_folder}") # Show user what they entered
    print(f"Output Excel files will be saved to: {output_export_directory}") # Show resolved output path
    
    all_organized_files_by_patient = find_and_organize_dicom_files(dicom_input_folder)
    run_dvh_export_process(all_organized_files_by_patient, output_export_directory)

    print(f"\nDVH export process finished for all patients.")
    print(f"Check the output directory: {output_export_directory}")
    print("Review console output and log messages for details, warnings, or errors.")
