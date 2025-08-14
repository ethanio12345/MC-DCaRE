#!/usr/bin/env python3
"""
CTDI Command-Line Interface for MC-DCaRE
==========================================

This script provides a command-line interface for running CTDI phantom validation
simulations without the GUI. Useful for testing and batch processing.

Usage:
    python run_ctdi.py --phantom 16 --kvp 100 --exposure 100 --histories 100000
    python run_ctdi.py --help  # Show all options

Output:
    Results are saved in runfolder/YYYY-MM-DD_HH-MM-SS/
    - dose_results.csv: Dose values at 5 positions
    - simulation.log: TOPAS execution log
    - configuration files: All TOPAS input files used
"""

import argparse
import os
import sys
from datetime import datetime
from src.runtime_handler import run_topas
from src.edits_handler import editor
from src.Energyspectrum import generate_new_topas_beam_profile
from src.defaultvalues import *

def create_run_directory():
    """Create timestamped run directory"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join("runfolder", timestamp)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(os.path.join(run_dir, "tmp"), exist_ok=True)
    return run_dir

def setup_ctdi_simulation(run_dir, args):
    """Configure CTDI simulation based on command-line arguments"""
    
    # Generate beam profile
    generate_new_topas_beam_profile(
        args.kvp, 
        args.exposure, 
        str(args.histories), 
        run_dir
    )
    
    # Copy and modify boilerplate files
    boilerplate_dir = "src/boilerplates"
    
    # Select phantom file
    phantom_file = f"CTDIphantom_{args.phantom}.txt"
    
    # Files to copy and modify
    files_to_copy = [
        "headsourcecode_boilerplate.txt",
        f"TOPAS_includeFiles/{phantom_file}",
        "TOPAS_includeFiles/fullfan.txt",
        "TOPAS_includeFiles/HUtoMaterialSchneider.txt",
        "TOPAS_includeFiles/Muen.dat",
        "TOPAS_includeFiles/NbParticlesInTime.txt"
    ]
    
    # Copy files to tmp directory
    for file in files_to_copy:
        src = os.path.join(boilerplate_dir, file)
        dst = os.path.join(run_dir, "tmp", os.path.basename(file))
        with open(src, 'r') as f_src, open(dst, 'w') as f_dst:
            f_dst.write(f_src.read())
    
    # Modify main configuration file
    head_file = os.path.join(run_dir, "tmp", "headsourcecode_boilerplate.txt")
    
    # Parameter mapping for replacements
    replacements = {
        "default_G4_Directory": args.g4_data,
        "default_TOPAS_Directory": args.topas_path,
        "default_Seed": str(args.seed),
        "default_Threads": str(args.threads),
        "default_Histories": str(args.histories),
        "default_IMAGEVOLTAGE": str(args.kvp) + " kV",
        "default_EXPOSURE": str(args.exposure) + " mAs",
        "default_FAN_MODE": args.fan_mode,
        "default_FIELD_X1": str(args.field_x1) + " cm",
        "default_FIELD_X2": str(args.field_x2) + " cm",
        "default_FIELD_Y1": str(args.field_y1) + " cm",
        "default_FIELD_Y2": str(args.field_y2) + " cm"
    }
    
    # Apply replacements
    for key, value in replacements.items():
        editor(head_file, key, value)
    
    return head_file

def main():
    parser = argparse.ArgumentParser(
        description="Run CTDI phantom validation simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ctdi.py --phantom 16 --kvp 100 --exposure 100
  python run_ctdi.py --phantom 32 --kvp 120 --exposure 200 --histories 500000
  python run_ctdi.py --phantom 16 --kvp 80 --exposure 50 --threads 4
        """
    )
    
    # Phantom selection
    parser.add_argument('--phantom', type=int, choices=[16, 32], default=16,
                        help='CTDI phantom diameter (16cm or 32cm)')
    
    # Beam parameters
    parser.add_argument('--kvp', type=float, default=100,
                        help='X-ray tube voltage in kV (default: 100)')
    parser.add_argument('--exposure', type=float, default=100,
                        help='Exposure in mAs (default: 100)')
    
    # Simulation parameters
    parser.add_argument('--histories', type=int, default=100000,
                        help='Number of particle histories (default: 100000)')
    parser.add_argument('--threads', type=int, default=1,
                        help='Number of CPU threads (default: 1)')
    parser.add_argument('--seed', type=int, default=9,
                        help='Random seed (default: 9)')
    
    # Field parameters
    parser.add_argument('--field-x1', type=float, default=14,
                        help='Field X1 size in cm (default: 14)')
    parser.add_argument('--field-x2', type=float, default=14,
                        help='Field X2 size in cm (default: 14)')
    parser.add_argument('--field-y1', type=float, default=10.7,
                        help='Field Y1 size in cm (default: 10.7)')
    parser.add_argument('--field-y2', type=float, default=10.7,
                        help='Field Y2 size in cm (default: 10.7)')
    
    # Fan mode
    parser.add_argument('--fan-mode', choices=['Full Fan', 'Half Fan'], default='Full Fan',
                        help='Beam collimation mode (default: Full Fan)')
    
    # Paths
    parser.add_argument('--g4-data', default=default_G4_Directory,
                        help='Geant4 data directory path')
    parser.add_argument('--topas-path', default=default_TOPAS_Directory,
                        help='TOPAS executable path')
    
    args = parser.parse_args()
    
    print("MC-DCaRE CTDI Command-Line Interface")
    print("=" * 40)
    print(f"Phantom: {args.phantom}cm")
    print(f"Beam: {args.kvp} kV, {args.exposure} mAs")
    print(f"Histories: {args.histories}")
    print(f"Threads: {args.threads}")
    print()
    
    # Create run directory
    run_dir = create_run_directory()
    print(f"Created run directory: {run_dir}")
    
    # Setup simulation
    print("Configuring simulation...")
    head_file = setup_ctdi_simulation(run_dir, args)
    
    # Run simulation
    print("Starting TOPAS simulation...")
    try:
        run_topas(head_file, run_dir)
        print("Simulation completed successfully!")
        print(f"Results saved in: {run_dir}")
    except Exception as e:
        print(f"Error running simulation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
