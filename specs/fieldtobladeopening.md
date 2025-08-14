# fieldtobladeopening.py

## Overview
This module converts field sizes into blade opening positions for the collimator. It handles the calculation of blade positions based on user-defined field dimensions.

## Functions

### calculate_blade_opening

**Parameters:**
- field_x1: float (field size X1 in cm)
- field_x2: float (field size X2 in cm)
- field_y1: float (field size Y1 in cm)
- field_y2: float (field size Y2 in cm)

**Process:**
Calculates blade positions using the formula:
x1 = field_x1 / 2
x2 = -field_x2 / 2
y1 = field_y1 / 2
y2 = -field_y2 / 2

**Returns:**
- Tuple of four floats (x1, x2, y1, y2) representing blade positions in cm.

**Example:**
```python
x1, x2, y1, y2 = calculate_blade_opening(14.0, 14.0, 10.7, 10.7)
```

## Usage
Used by the GUI to update blade positions when field sizes are modified. Also used by edits_handler.py when generating configuration files.

## Dependencies
- Used by topas_gui.py and edits_handler.py.
