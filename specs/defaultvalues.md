# defaultvalues.py

## Overview
This file contains default configuration values used throughout the application. These values are loaded when the GUI starts and can be modified by the user through the interface.

## Key Variables
- default_G4_Directory: Path to the Geant4 data directory.
- default_TOPAS_Directory: Path to the TOPAS executable.
- default_Seed: Random seed for simulations.
- default_Threads: Number of CPU threads to use.
- default_Histories: Number of particle histories per simulation.
- default_DICOM_Directory: Default directory for DICOM files.
- default_DICOM_RP_file: Default path for DICOM RP (Radiation Plan) files.
- default_DICOM_TRANS_X/Y/Z: Default translation values for DICOM alignment.
- default_DICOM_ROT_X/Y/Z: Default rotation values for DICOM alignment.
- default_DICOM_ISOCENTER_X/Y/Z: Default isocenter coordinates.
- default_DTM_Zbins: Number of Z bins for DTM.
- default_TLE_Zbins: Number of Z bins for TLE.
- default_DTW_Zbins: Number of Z bins for DTW.
- default_COUCH_HLZ: Couch height along Z axis.
- default_COUCH_HLY: Couch height along Y axis.
- default_COUCH_HLX: Couch height along X axis.
- default_TIME_SEQ_TIME: Time sequence duration.
- default_TIME_VERBOSITY: Verbosity level for time output.
- default_TIME_TIME_END: End time for simulation.
- default_TIME_ROT_FUNC: Rotation function type.
- default_TIME_ROT_RATE: Rotation rate.
- default_TIME_ROT_START: Initial rotation angle.
- default_TIME_ROT_HISTORY: Histories per rotation.
- default_FAN_MODE: Beam collimation mode (Full Fan or Half Fan).
- default_FIELD_X1/X2: Field sizes along X axis.
- default_FIELD_Y1/Y2: Field sizes along Y axis.
- default_BLADE_X1/X2: Blade positions along X axis.
- default_BLADE_Y1/Y2: Blade positions along Y axis.
- default_IMAGE_START_ANGLE: Starting angle for imaging.
- default_IMAGE_VOLTAGE: Imaging voltage.
- default_EXPOSURE: Exposure time.

## Usage
These variables are imported by other modules to set default values in the GUI and simulation configurations. Users can modify these values through the GUI, which will override the defaults.

## Dependencies
- Used by topas_gui.py, runtime_handler.py, edits_handler.py, and others.
