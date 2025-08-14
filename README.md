# MC-DCaRE: Monte Carlo Dose Calculation and Research Environment

## System Overview
MC-DCaRE is a comprehensive tool for performing Monte Carlo dose calculations using TOPAS (based on Geant4). It provides both a GUI interface and command-line capabilities for configuring and running simulations. The system supports both patient-specific dose calculations using DICOM data and CTDI phantom validation studies.

## Key Features
- **Graphical User Interface (GUI)**: Intuitive interface for setting simulation parameters
- **DICOM Support**: Loads patient DICOM images and treatment plans
- **CTDI Validation**: Simulates CT dose index measurements
- **Beam Profile Generation**: Creates X-ray energy spectra using spekpy
- **Parallel Execution**: Runs simulations concurrently using multiprocessing
- **Detailed Logging**: Generates comprehensive logs and output files

## Installation & Setup
### Requirements
- **Operating System**: Ubuntu (Linux)
- **Python**: 3.x
- **Dependencies**: 
  - FreeSimpleGUI
  - pydicom
  - spekpy
  - numpy
- **TOPAS**: Must be installed with Geant4 data

### Configuration
1. **Set G4Data Directory**:
   - Edit `src/defaultvalues.py` and set `default_G4_Directory` to your Geant4 data path.
2. **Set TOPAS Directory**:
   - Edit `src/defaultvalues.py` and set `default_TOPAS_Directory` to your TOPAS executable path.

## Workflow Documentation
### GUI Workflow
1. **Launch Application**:
   ```bash
   python topas_gui.py
   ```
2. **Main Tab**:
   - Set simulation parameters (kVp, exposure, field sizes, etc.)
3. **Simulation Settings Tab**:
   - Configure TOPAS and Geant4 paths
   - Set number of histories and threads
4. **DICOM Tab**:
   - Load DICOM image sets and treatment plans
   - Extract isocenter coordinates
5. **CTDI Tab**:
   - Select phantom type (16cm or 32cm)
   - Configure CTDI simulation parameters
6. **Run Simulation**:
   - Click "Run" to start simulation
   - Results are saved in `runfolder/YYYY-MM-DD_HH-MM-SS/`

### CTDI Command-Line Interface
For non-GUI testing, use the `run_ctdi.py` script (to be implemented separately).

## Output Interpretation
### Directory Structure
```
runfolder/
    YYYY-MM-DD_HH-MM-SS/
        tmp/
            headsourcecode.txt
            CTDIphantom_16.txt
            ...
        dose_results.csv
        simulation.log
        ...
```

### Key Files
- **dose_results.csv**: Contains dose values at 5 measurement positions (center, top, bottom, left, right)
- **simulation.log**: TOPAS execution log with detailed simulation output
- **headsourcecode.txt**: Main TOPAS configuration file used for the simulation

## Boilerplate System
The system uses boilerplate files stored in `src/boilerplates/` which are copied to the `tmp/` directory of each run and modified as needed. Key files include:
- `headsourcecode_boilerplate.txt`: Main configuration template
- `CTDIphantom_16.txt` / `CTDIphantom_32.txt`: Phantom geometry definitions
- `HUtoMaterialSchneider.txt`: Hounsfield Unit to material conversion table

## Troubleshooting Guide
### Common Errors
1. **DICOM Loading Error**:
   - Check DICOM directory path in `defaultvalues.py`
   - Ensure DICOM files are in a supported format
2. **TOPAS Path Error**:
   - Verify `default_TOPAS_Directory` in `defaultvalues.py`
   - Ensure TOPAS executable is in the specified path
3. **Beam Profile Generation Error**:
   - Check `Energyspectrum.py` for correct parameter handling
   - Verify `spekpy` installation

### Debugging Steps
- Check temporary files in `tmp/` directory:
  ```bash
  ls -l tmp/
  cat tmp/headsourcecode.txt
  ```
- Verify simulation parameters in `headsourcecode.txt`

## Key Components Reference
### topas_gui.py
- Main application entry point
- Handles GUI setup and event loop
- Manages simulation execution

### runtime_handler.py
- Manages simulation runs
- Handles parallel execution
- Logs simulation output

### edits_handler.py
- Modifies TOPAS configuration files
- Handles string replacements in boilerplate files

### Energyspectrum.py
- Generates X-ray beam profiles
- Uses spekpy to calculate energy spectra

### defaultvalues.py
- Stores default configuration values
- Paths, simulation parameters, DICOM settings

## Future Improvements
- Template management system for boilerplate files
- Enhanced CLI interface with more options
- Improved error handling and user feedback

## License
This project is licensed under the terms of the MIT License. See LICENSE for details.
