import os
import csv
import pydicom 
from dicompylercore import dicomparser, dvhcalc, dvh #issue here

def main():
    # Set your DICOM folder paths
    dicom_dir = "/home/jkgan/Test_dicom_bug_issue/IMDOSE_B5"
    # rtstruct_file = "RS.1.2.246.352.221.4847784370425692620.9260382362699022517.dcm"
    # rtdose_file = "RTDOSE_2cbct.dcm"
    # rtplan_file = "RP.1.2.246.352.221.5456952295308318909.8548390088644948922.dcm"  # Optional

    rtstruct_file = None
    rtdose_file = None

    for f in os.listdir(dicom_dir):
        path = os.path.join(dicom_dir, f)
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            if ds.Modality == "RTSTRUCT":
                rtstruct_file = path
            elif ds.Modality == "RTDOSE":
                rtdose_file = path
        except:
            continue

    if not rtstruct_file or not rtdose_file:
        raise FileNotFoundError("RTSTRUCT or RTDOSE file not found.")

    # --- Load using dicompyler-core ---
    rtss = dicomparser.DicomParser(rtstruct_file)
    # dose = dicomparser.DicomParser(rtdose_file)
    structures = rtss.GetStructures()
    # print(structures)


    # Only keep structures with defined contours
    roi_contours = getattr(rtss.ds, "ROIContourSequence", [])
    defined_structure_ids = [roi.ReferencedROINumber for roi in roi_contours]


    # --- Output to CSV ---
    with open("DVHs.csv", mode="w", newline="") as csv_file:
        fieldnames = ["Structure", "Volume (cc)", "Dose (Gy)", "Volume (%)"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for structure_id, structure in structures.items():
            name = structure.get("name", f"ID_{structure_id}")
            if structure_id not in defined_structure_ids:
                print(f"Skipping {name} — no contour found.")
                continue

            try:
                # print(structure_id)
                print(structure_id)
                dvh = dvhcalc.get_dvh(rtstruct_file, rtdose_file,  structure_id)
                print(dvh)
                if dvh is None:
                    print(f"DVH not computed for {name}")
                    continue

                for dose_val, vol_val in zip(dvh.dose, dvh.volume):
                    writer.writerow({
                        "Structure": name,
                        "Volume (cc)": round(dvh.volume_cc, 2),
                        "Dose (Gy)": round(dose_val, 2),
                        "Volume (%)": round(vol_val, 2)
                    })

                print(f"✓ Exported DVH for: {name}")

            except Exception as e:
                print(f"⚠️ Could not compute DVH for {name} (ID {structure_id}): {e}")
                continue

    print("\n🎉 DVHs exported to DVHs.csv successfully.")


def mini_test():
    # dicom_dir = "/home/jkgan/Test_dicom_bug_issue/IMDOSE_B5"
    rtstruct_file = "/home/jkgan/Test_dicom_bug_issue/IMDOSE_B5/RS.1.2.246.352.221.4847784370425692620.9260382362699022517.dcm"
    rtdose_file = "/home/jkgan/Test_dicom_bug_issue/IMDOSE_B5/RTDOSE_2cbct.dcm"
    # rtplan_file = "RP.1.2.246.352.221.5456952295308318909.8548390088644948922.dcm"  # Optional

    # for f in os.listdir(dicom_dir):
    #     path = os.path.join(dicom_dir, f)
    #     try:
    #         ds = pydicom.dcmread(path, stop_before_pixels=True)
    #         if ds.Modality == "RTSTRUCT":
    #             rtstruct_file = path
    #         elif ds.Modality == "RTDOSE":
    #             rtdose_file = path
    #     except:
    #         continue
    
    # rtss = dicomparser.DicomParser(rtstruct_file)
    # dose = dicomparser.DicomParser(rtdose_file)
    # structures = rtss.GetStructures()
    # roi_contours = getattr(rtss.ds, "ROIContourSequence", [])
    # defined_structure_ids = [roi.ReferencedROINumber for roi in roi_contours]
    dvh = dvhcalc.get_dvh(rtstruct_file, rtdose_file,  5)
    print(dvh)


if __name__ == '__main__':
    # main()
    mini_test()