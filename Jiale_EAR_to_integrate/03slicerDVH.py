import os
import slicer
import slicer.util

# ──────────────────────────────────────────────────────────────────────────────
# 1. Base output folder (change as needed)
baseDir = r"/home/dro/Desktop/jiale/imaging_dosimetry (dvh export)/2025.05.20/VMAT/VMAT2"
if not os.path.isdir(baseDir):
    os.makedirs(baseDir)

# 2. Initialise the DVH logic and create a parameter node
dvhLogic  = slicer.modules.dosevolumehistogram.logic()
paramNode = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLDoseVolumeHistogramNode", "BatchDVHParams"
)

# 3. Find your segmentation node by substring (case-insensitive)
segNode = None
for n in slicer.util.getNodesByClass('vtkMRMLSegmentationNode'):
    if "ct-17/02/25" in n.GetName().lower():
        segNode = n
        break
if not segNode:
    raise RuntimeError("Could not find segmentation with 'CT-17/02/25' in its name")
print("Using segmentation:", segNode.GetName())

# 3a. Ensure the segmentation has a display node, and make all segments visible
dispNode = segNode.GetDisplayNode()
if not dispNode:
    segNode.CreateDefaultDisplayNodes()
    dispNode = segNode.GetDisplayNode()
dispNode.SetAllSegmentsVisibility(True)
print("  → All segments set to visible")

# 4. Loop through every dose volume (scalar volume) in the scene
for doseNode in slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode'):
    doseName = doseNode.GetName()
    print(f"\n→ Computing DVH for: {doseName}")

    # snapshot existing tables
    existingTableIDs = {t.GetID() for t in slicer.util.getNodesByClass('vtkMRMLTableNode')}

    # point paramNode at this dose + segmentation
    paramNode.SetAndObserveDoseVolumeNode(doseNode)
    paramNode.SetAndObserveSegmentationNode(segNode)

    # compute the DVH
    err = dvhLogic.ComputeDvh(paramNode)
    if err:
        print(f"   • Skipped (ComputeDvh error): {err}")
        continue

    # collect new DVH tables
    allTables = slicer.util.getNodesByClass('vtkMRMLTableNode')
    newTables = [t for t in allTables if t.GetID() not in existingTableIDs]
    if not newTables:
        print("   • Warning: no new DVH tables found")
        continue

    # 6. Combine all ROIs into one CSV
    safeDoseName = doseName.replace(" ", "_").replace(":", "").replace("[", "").replace("]", "")
    combinedPath = os.path.join(baseDir, f"{safeDoseName}.csv")

    # build header row (two columns per ROI)
    headers = []
    for curveTable in newTables:
        # take the table's own column names (e.g. "Dose", "Volume")
        for c in range(curveTable.GetNumberOfColumns()):
            headers.append(curveTable.GetColumnName(c))
    # write out
    maxRows = max(t.GetNumberOfRows() for t in newTables)
    with open(combinedPath, 'w', newline='') as f:
        f.write(','.join(headers) + '\n')
        for row in range(maxRows):
            rowValues = []
            for t in newTables:
                nRows = t.GetNumberOfRows()
                nCols = t.GetNumberOfColumns()
                if row < nRows:
                    rowValues.extend(t.GetCellText(row, c) for c in range(nCols))
                else:
                    rowValues.extend('' for _ in range(nCols))
            f.write(','.join(rowValues) + '\n')

    print(f"   • Combined CSV written: {combinedPath}")

print("\nAll done!")
