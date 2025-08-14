# imaging_modes_lookuptable.py

## Overview
This module contains lookup tables for different imaging modes, possibly mapping mode names to specific configuration parameters or settings.

## Key Variables

- **imaging_modes**: Dictionary mapping mode names to configuration parameters.
  - Example:
    - "Image Gently": {"voltage": "100 kV", "exposure": "100 mAs", ...}
    - "Head": {"voltage": "120 kV", "exposure": "120 mAs", ...}

## Usage

Used by the GUI to populate imaging mode options and apply corresponding settings when selected. The lookup tables are used to set parameters like voltage, exposure, and imaging angles.

## Dependencies

- Used by topas_gui.py to update imaging parameters in the GUI.
- Used by edits_handler.py when modifying configuration files with imaging parameters.
