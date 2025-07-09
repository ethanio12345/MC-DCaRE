import os
import numpy as np
import slicer
import slicer.util

# ──────────────────────────────────────────────────────────────────────────────
# 1. Base output folder (change as needed)
baseDir = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/VMAT/VMAT2"
os.makedirs(baseDir, exist_ok=True)

# 2. Find your segmentation node by substring (case-insensitive)
segNode = None
for n in slicer.util.getNodesByClass('vtkMRMLSegmentationNode'):
    if "ct-17/02/25" in n.GetName().lower():
        segNode = n
        break
if not segNode:
    raise RuntimeError("Could not find segmentation with 'CT-17/02/25' in its name")
print("Using segmentation:", segNode.GetName())

# 3. Ensure display node and make all segments visible
dispNode = segNode.GetDisplayNode() or segNode.CreateDefaultDisplayNodes() or segNode.GetDisplayNode()
dispNode.SetAllSegmentsVisibility(True)

# 4. Compute each segment’s volume (cc)
labelmapVol = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segNode, labelmapVol)
arr = slicer.util.arrayFromVolume(labelmapVol)
spacing = np.array(labelmapVol.GetSpacing())
voxelVol = spacing.prod()  # mm³ per voxel

segmentation = segNode.GetSegmentation()
segVolumesCc = {}
for segID in segmentation.GetSegmentIDs():
    seg = segmentation.GetSegment(segID)
    count = int((arr == seg.GetLabelValue()).sum())
    segVolumesCc[seg.GetName()] = (count * voxelVol) / 1000.0   # store by ROI name

slicer.mrmlScene.RemoveNode(labelmapVol)

# 5. Initialise DVH logic
dvhLogic  = slicer.modules.dosevolumehistogram.logic()
paramNode = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLDoseVolumeHistogramNode", "BatchDVHParams"
)

# 6. Loop through every dose volume
for doseNode in slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode'):
    doseName = doseNode.GetName()
    if "unnamed series" in doseName.lower():
        print(f"→ Skipping dose volume: {doseName!r}")
        continue
    print(f"\n→ Computing DVH for: {doseName}")

    # snapshot existing table IDs
    existingIDs = {t.GetID() for t in slicer.util.getNodesByClass('vtkMRMLTableNode')}

    # compute DVH
    paramNode.SetAndObserveDoseVolumeNode(doseNode)
    paramNode.SetAndObserveSegmentationNode(segNode)
    err = dvhLogic.ComputeDvh(paramNode)
    if err:
        print(f"   • Skipped (ComputeDvh error): {err}")
        continue

    # collect *only* the curve tables (Dose+Volume)
    allTables = slicer.util.getNodesByClass('vtkMRMLTableNode')
    curveTables = []
    for t in allTables:
        if t.GetID() in existingIDs:
            continue
        # filter for exactly two columns and first is “Dose”
        if t.GetNumberOfColumns()==2 and t.GetColumnName(0).lower()=="dose":
            curveTables.append(t)
    if not curveTables:
        print("   • Warning: no DVH curve tables found")
        continue

    # 7. Combine curves into CSV, enriching headers
    safeDose = doseName.replace(" ", "_").replace(":", "").replace("[", "").replace("]", "")
    outPath = os.path.join(baseDir, f"{safeDose}.csv")

    # build headers with ROI name + volume
    headers = []
    segmentIDs = segmentation.GetSegmentIDs()
    for idx, table in enumerate(curveTables):
        roiName = segmentation.GetSegment(segmentIDs[idx]).GetName()
        vol_cc = segVolumesCc.get(roiName, 0.0)
        for col in range(2):
            base = table.GetColumnName(col)  # “Dose” or “Volume”
            headers.append(f"{base} - {roiName} ({vol_cc:.1f}cc)")

    # write CSV
    maxRows = max(t.GetNumberOfRows() for t in curveTables)
    with open(outPath, 'w', newline='') as f:
        f.write(','.join(headers) + '\n')
        for row in range(maxRows):
            vals = []
            for t in curveTables:
                if row < t.GetNumberOfRows():
                    vals.extend(t.GetCellText(row, c) for c in range(2))
                else:
                    vals.extend(['',''])
            f.write(','.join(vals) + '\n')

    print(f"   • Combined CSV written: {outPath}")

print("\nAll done!")

