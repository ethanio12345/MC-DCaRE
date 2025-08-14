# Energyspectrum.py

## Overview
This file is responsible for generating X-ray beam energy spectra for TOPAS simulations using the spekpy library. It handles the creation of beam profiles based on user-defined parameters such as kVp and exposure.

## Functions

### generate_new_topas_beam_profile

**Parameters:**
- anode_voltage: float (kV)
- exposure: float (mAs)
- Histories: int
- path: str (output directory)

**Process:**
1. Uses spekpy to generate an unfiltered spectrum at 1mm Al.
2. Calculates fluence and number of particles.
3. Computes calibration factor = particles / Histories.
4. Writes calibration factor to head_calibration_factor.txt.
5. Normalizes and trims spectrum.
6. Converts to TOPAS format and writes to ConvertedTopasFile.txt.

**Outputs:**
- head_calibration_factor.txt: Calibration factor and input parameters.
- ConvertedTopasFile.txt: TOPAS-formatted spectrum.

**Example:**
```python
generate_new_topas_beam_profile(100.0, 100.0, 100000, "/output")
```

## Dependencies
- Uses spekpy and numpy.
- Called by runtime_handler.py when generating beam profiles.
- Used in GUI when user updates imaging parameters.
