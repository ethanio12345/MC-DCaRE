# guilayers.py

## Overview
This module defines the layout and components of the graphical user interface. It organizes the GUI into tabs and elements, providing a structured way to present parameters to the user.

## Key Variables

- **main_layout**: Defines the main window layout with tabs for different functionalities.
- **settings_layout**: Contains settings inputs like G4 directory, TOPAS directory, etc.
- **dicom_layout**: Includes inputs for DICOM patient data, such as directory, RP file, and alignment parameters.
- **ctdi_layout**: Contains inputs for CTDI phantom validation, including phantom size, Z bins, etc.
- **imaging_layout**: Includes imaging parameters like kVp, exposure, and imaging mode.
- **simulation_layout**: Contains simulation parameters like seed, threads, histories, etc.
- **blade_layout**: Includes blade position inputs derived from field sizes.

## Usage

Imported by topas_gui.py to create the GUI window. The layouts are combined into a single window using FreeSimpleGUI.

## Dependencies

- Used by topas_gui.py to build the user interface.
- Layouts are used to organize components and handle user inputs.
