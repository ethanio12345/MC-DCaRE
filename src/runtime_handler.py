# This script is used to handle all the initialisation and running of the simulations. It will set up a date and timestamped folder in /runfolder and copy all the relevant files from /tmp and /src over into it
# The duplication of the files are intended, this will allow for users to rerun the script as it was in case of downstream changes in the future or for reevaluation. 
# Future improvments would be to add in an logging function that logs the console output at runtime. This would allow for easier debugging and integrate a progress bar that watches the number of histories left to completion. 
import os
from datetime import datetime
import shutil
import subprocess
import multiprocessing as mp
from typing import List

def run_topas(x1: List[List[str]]) -> None:
    """This function exist so that a nested list of commands can be parsed and scheduled to be processed asyncro

    Args:
        x1 (List[List[str]]): A nested list of commands to be ran with the topas executable. The outer list contains the commands and the inner list contains the arguments to the command.

    Returns:
        None
    """
    command = x1[0][0]
    rundatadir = x1[1][0]
    subprocess.run("cd " + rundatadir, shell=True)
    # result = subprocess.run(command, cwd= rundatadir, shell =True, capture_output=True, text=True)
    # print(result.stdout) #Gives console output as as text chunk, for logging 
    result = subprocess.run(command, cwd= rundatadir, shell =True) #for instant console output 
    print('ran')

def plugsgenerator(phantomsize: str, rundatadir: str, topas_application_path: str) -> List[List[List[str]]]:
        '''
        This function is only used for CTDI to generate 5 files to simulation the placement of a detector on the 5 possible plug positions.
        Returns a nested list of commands to be ran to multi process all 5 files together.
        '''
        path = os.getcwd()
        plugs_position = ['ChamberPlugCentre', 'ChamberPlugTop', 'ChamberPlugBottom', 'ChamberPlugLeft', 'ChamberPlugRight']
        commands = []
        for position in plugs_position:
                file1 = open(path + '/tmp/headsourcecode.txt', 'r')
                if phantomsize == 'ctdi16':
                        file2 = open(path +'/tmp/CTDIphantom_16.txt', 'r')
                if phantomsize == 'ctdi32':
                        file2 = open(path +'/tmp/CTDIphantom_32.txt', 'r')
                content1 = file1.read()
                file1.close()
                content2 = file2.read()
                file2.close()
                combinedtext= open(path +'/tmp/plugsourcecode.txt', 'w')
                combinedtext.write(content1 +content2)
                # The above chunk combines the CTDI phantom file into headsourcecode as TOPAS throws error due to some unknown default chaining issue. 
                positionfile = rundatadir + '/'+ position + '.txt'
                shutil.copy(path + '/tmp/plugsourcecode.txt', positionfile)
                search_text1 = '@@PLACEHOLDER@@'
                replace_text1 = position
                search_text2 = 's:Ge/'+ position + '/Material="PMMA"'
                replace_text2 = 's:Ge/'+ position + '/Material="Air"'
                with open(path +'/tmp/plugsourcecode.txt', 'r') as file:
                        file_data = file.read()
                        file_data = file_data.replace(search_text1, replace_text1)
                        file_data = file_data.replace(search_text2, replace_text2)
                with open(positionfile, 'w') as file:
                        file.write(file_data)
                commands.append([[topas_application_path + ' ' + rundatadir + '/'+ position + '.txt'], [rundatadir]])        
        return commands

def log_output(
        input_file_path: str,
        tag: str,
        topas_application_path: str,
        fan_tag: str
    ) -> str:
    """This function runs a TOPAS simulation using multiprocessing.

    Args:
        input_file_path (str): The file path of the input file.
        tag (str): A tag that determines which type of simulation is to be run.
        topas_application_path (str): The file path of the TOPAS executable.
        fan_tag (str): A tag that determines which fan type is to be used.

    Returns:
        str: A string indicating the status of the simulation.
    """
    rundatadir = os.path.join(
        os.getcwd(), "runfolder", datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(rundatadir, exist_ok=True)
    shutil.copy(input_file_path, rundatadir)
    path = os.getcwd()

    def copy_common_files():
        common_files = [
            'Muen.dat',
            'NbParticlesInTime.txt',
            'ConvertedTopasFile.txt',
            'head_calibration_factor.txt'
        ]
        for file in common_files:
            shutil.copy(os.path.join(path, 'src/boilerplates/TOPAS_includeFiles', file), rundatadir)

    def copy_fan_file():
        fan_file = 'fullfan.txt' if fan_tag == 'Full Fan' else 'halffan.txt'
        shutil.copy(os.path.join(path, 'src/boilerplates/TOPAS_includeFiles', fan_file), rundatadir)

    pool_size = mp.cpu_count() - 1

    if tag == 'dicom':
        shutil.copy(os.path.join(path, 'src/boilerplates/TOPAS_includeFiles', 'HUtoMaterialSchneider.txt'), rundatadir)
        copy_fan_file()
        shutil.copy(os.path.join(path, 'tmp', 'headsourcecode.txt'), rundatadir)
        shutil.copy(os.path.join(path, 'tmp', 'patientDICOM.txt'), rundatadir)
        command = [f"{topas_application_path} {rundatadir}/headsourcecode.txt"]
        with mp.Pool(pool_size) as pool:
            pool.map_async(run_topas, [(command, [rundatadir])])
            pool.close()
            pool.join()
        run_status = "DICOM simulation completed"

    elif tag in ['ctdi16', 'ctdi32']:
        copy_common_files()
        copy_fan_file()
        commands = plugsgenerator(tag, rundatadir, topas_application_path)
        with mp.Pool(pool_size) as pool:
            pool.map_async(run_topas, commands)
            pool.close()
            pool.join()
        run_status = "CTDI simulation completed"

    else:
        run_status = 'Error encountered'

    return run_status

if __name__ == "__main__":
    pass
    