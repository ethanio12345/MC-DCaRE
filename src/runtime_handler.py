# This script is used to handle all the initialisation and running of the simulations. It will set up a date and timestamped folder in /runfolder and copy all the relevant files from /tmp and /src over into it
# The duplication of the files are intended, this will allow for users to rerun the script as it was in case of downstream changes in the future or for reevaluation. 
# Future improvments would be to add in an logging function that logs the console output at runtime. This would allow for easier debugging and integrate a progress bar that watches the number of histories left to completion. 
import os
from datetime import datetime
import shutil
import subprocess
import multiprocessing as mp

def run_topas(x1):
        # This function exist so that a nested list of commands can be parsed and scheduled to be processed asyncro
        command = x1[0][0]
        rundatadir = x1[1][0]
        subprocess.run("cd " + rundatadir, shell=True)
        # result = subprocess.run(command, cwd= rundatadir, shell =True, capture_output=True, text=True)
        # print(result.stdout) #Gives console output as as text chunk, for logging 
        result = subprocess.run(command, cwd= rundatadir, shell =True) #for instant console output 
        print('ran')

def plugsgenerator(phantomsize: str , rundatadir: str , topas_application_path: str): 
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

def log_output(input_file_path, tag, topas_application_path, fan_tag):
        rundatadir = os.path.join(
                os.getcwd() +"/runfolder",
                datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(rundatadir) #creates a folder marked by date and time 
        shutil.copy(input_file_path, rundatadir)
        path = os.getcwd()
        
        if tag == 'dicom':
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/HUtoMaterialSchneider.txt', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
                if fan_tag == 'Full Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
                elif fan_tag == 'Half Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
                shutil.copy(path + '/tmp/ConvertedTopasFile.txt', rundatadir)
                shutil.copy(path + '/tmp/head_calibration_factor.txt', rundatadir)
                shutil.copy(path + '/tmp/headsourcecode.txt', rundatadir)
                shutil.copy(path + '/tmp/patientDICOM.txt', rundatadir)

                command = [topas_application_path + ' ' + rundatadir + '/headsourcecode.txt']

                subprocess.run("cd " + rundatadir, shell=True)
                result = subprocess.run(command, cwd= rundatadir, shell =True) #for instant console output 

                run_status= "DICOM simulation completed"

        elif tag == 'ctdi16' or tag == 'ctdi32':
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
                shutil.copy(path + '/tmp/ConvertedTopasFile.txt', rundatadir)
                shutil.copy(path + '/tmp/head_calibration_factor.txt', rundatadir)
                if fan_tag == 'Full Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
                elif fan_tag == 'Half Fan':
                       shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
                
                if tag == 'ctdi16':
                       commands = plugsgenerator('ctdi16', rundatadir, topas_application_path)
                elif tag == 'ctdi32':
                       commands =plugsgenerator('ctdi32', rundatadir, topas_application_path)

                pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
                pool.map_async(run_topas, commands)
                pool.close()
                pool.join()
                run_status= "CTDI simulation completed" 

        # elif tag == 'ctdi32':
        #         shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/Muen.dat', rundatadir)
        #         shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/NbParticlesInTime.txt', rundatadir)
        #         shutil.copy(path + '/tmp/ConvertedTopasFile.txt', rundatadir)
        #         shutil.copy(path + '/tmp/head_calibration_factor.txt', rundatadir)

        #         if fan_tag == 'Full Fan':
        #                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/fullfan.txt', rundatadir)
        #         elif fan_tag == 'Half Fan':
        #                shutil.copy(path + '/src/boilerplates/TOPAS_includeFiles/halffan.txt', rundatadir)
        #         commands =plugsgenerator('ctdi32', rundatadir, topas_application_path)

        #         pool = mp.Pool(60) #How to best tune this? Currently taking it as -1 of max cpu count 
        #         pool.map_async(run_topas, commands)
        #         pool.close()
        #         pool.join()
        #         run_status= "CTDI simulation completed" 

        else:
              run_status = 'Error encountered' 

        return run_status

if __name__ == "__main__":
    pass
    