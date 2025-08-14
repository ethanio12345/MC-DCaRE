# topas_gui.py

## Overview
This is the main application file that sets up the graphical user interface and handles user interactions. It initializes the GUI, manages event handling, and coordinates the execution of simulations.

## Key Components

- **Main Window**: Uses FreeSimpleGUI to create the GUI layout with tabs for different functionalities.
- **Event Loop**: Continuously checks for user inputs and triggers corresponding actions.
- **Simulation Controls**: Buttons and inputs that initiate simulation runs via runtime_handler.
- **Settings**: Allows users to modify default values from defaultvalues.py.
- **Imaging Parameters**: Inputs for kVp, exposure, etc., that trigger beam profile generation.

## Usage

The entry point for the application. Users run this script to start the GUI. The main event loop handles user interactions and updates the GUI accordingly.

## Dependencies

- Imports and uses functions from:
  - edits_handler: editor() for modifying configuration files
  - runtime_handler: log_output() for running simulations
  - Energyspectrum: generate_new_topas_beam_profile() for beam profiles
  - fieldtobladeopening: calculate_blade_opening() for blade positions
  - defaultvalues: for default configuration values
  - guilayers: for GUI layout components
