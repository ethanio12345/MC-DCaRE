# Script for 3D Slicer Python Interactor to create empty dose volumes
# Named: 1cbct+oof, 1kvkv+oof, 2cbct+oof, 2kckc+oof
# Paste this into the Python Interactor (Ctrl+3) in Slicer

import slicer

# List of placeholder volume names
names = ["1cbct+oof", "1kvkv+oof", "2cbct+oof", "2kvkv+oof"]

for name in names:
    # Create a new empty scalar volume node
    volNode = slicer.vtkMRMLScalarVolumeNode()
    volNode.SetName(name)
    # Optionally, to match geometry of an existing dose volume, uncomment and set reference:
    # ref = slicer.util.getNode('YourReferenceDoseName')
    # volNode.SetIJKToRASMatrix(ref.GetIJKToRASMatrix())
    slicer.mrmlScene.AddNode(volNode)

print(f"Created dose volume placeholders: {', '.join(names)}")
