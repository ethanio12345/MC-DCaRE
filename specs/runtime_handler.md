# runtime_handler.py

## Overview
This module manages the execution of TOPAS simulations, including parallel processing, logging, and result handling. It handles the setup and execution of simulations, both for DICOM patient data and CTDI phantom validation.

## Functions

### run_topas

**Parameters:**
- head_file: str (path to main configuration file)
- run_dir: str (run directory)

**Process:**
1. Executes TOPAS using the specified configuration file.
2. Captures and logs the output.
3. Handles errors and simulation completion.

### plugsgenerator

**Parameters:**
- phantomsize: str ('ctdi16' or 'ctdi32')
- rundatadir: str (run directory path)
- topas_application_path: str (path to TOPAS executable)

**Process:**
Generates plugin configuration files for the specified phantom size and returns a list of commands to run.

**Returns:**
- List of lists containing commands and run directories.

### log_output

**Parameters:**
- input_file_path: str (path to input file)
- tag: str ('dicom', 'ctdi16', 'ctdi32')
- topas_application_path: str (path to TOPAS executable)
- fan_tag: str ('Full Fan' or 'Half Fan')

**Process:**
1. Creates a timestamped run directory.
2. Copies necessary files to the run directory.
3. Runs simulations in parallel using the pool.
4. Returns run status.

**Returns:**
- run_status: str (e.g., "DICOM simulation completed")

## Usage
Called by topas_gui.py to execute simulations. Also used in the CTDI command-line interface.

## Dependencies
- Uses edits_handler.py to modify configuration files.
- Uses Energyspectrum.py to generate beam profiles.
- Used by topas_gui.py and possibly other modules.
