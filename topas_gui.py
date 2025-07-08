import os
import FreeSimpleGUI as sg
import shutil
from pydicom import dcmread
from src.runtime_handler import log_output
from src.edits_handler import editor
from src.guilayers import *
from src.imaging_modes_lookuptable import imaging_modes_lookup
from src.Energyspectrum import generate_new_topas_beam_profile

#Useful functions###################################################
def reset_tmp():
    '''
    Helper function that resets the temporary files after each run to ensure smooth operation. 
    '''
    path = os.getcwd()
    #generate a headsource file from a boiler plate so we edit only that copy each time
    original_headsource_file_path = path + '/src/boilerplates/headsourcecode_boilerplate.txt'
    duplicate_headsource_file_path = path + "/tmp/headsourcecode.txt"
    shutil.copy(original_headsource_file_path, duplicate_headsource_file_path)

    #generate a dicom includefile from a boiler plate so we edit only that copy each time
    original_dicom_file_path = path + '/src/boilerplates/TOPAS_includeFiles/patientDICOM.txt'
    duplicate_dicom_file_path = path + "/tmp/patientDICOM.txt"
    shutil.copy(original_dicom_file_path, duplicate_dicom_file_path)

    #generate a CTDI 16cm includefile from a boiler plate so we edit only that copy each time
    original_CTDI_16_file_path = path + '/src/boilerplates/TOPAS_includeFiles/CTDIphantom_16.txt'
    duplicate_CTDI_16_file_path = path + "/tmp/CTDIphantom_16.txt"
    shutil.copy(original_CTDI_16_file_path, duplicate_CTDI_16_file_path)

    #generate a CTDI 32cm includefile from a boiler plate so we edit only that copy each time
    original_CTDI_32_file_path = path + '/src/boilerplates/TOPAS_includeFiles/CTDIphantom_32.txt'
    duplicate_CTDI_32_file_path = path + "/tmp/CTDIphantom_32.txt"
    shutil.copy(original_CTDI_32_file_path, duplicate_CTDI_32_file_path)

    # #generate a blank head_calibration file a boiler plate so we edit only that copy each time
    # original_headcali_file_path = path + '/src/head_calibration_factor_boilerplate.txt'
    # duplicate_headcali_file_path = path + "/tmp/head_calibration_factor.txt"
    # shutil.copy(original_headcali_file_path, duplicate_headcali_file_path)

    #generate a blank convertedtopas includefile from a boiler plate so we edit only that copy each time
    # original_convertedtopas_file_path = path + '/src/boilerplates/TOPAS_includeFiles/ConvertedTopasFile_boilerplate.txt'
    # duplicate_convertedtopas_file_path = path + "/tmp/ConvertedTopasFile.txt"
    # shutil.copy(original_convertedtopas_file_path, duplicate_convertedtopas_file_path)


def quantity_unit_stripper(string_value):
    ''' 
    Helper script to split an input into its float value and string. Eg string_value = '-5 cm' will return -5 , 'cm'
    This assumes the value comes in the form of float(quantity)`whitespace`str(unit)
    '''
    # quantity = []
    # unit = []
    for t in string_value.split():
        try:
            quantity = float(t) 
        except ValueError:
            unit = t
    return quantity , unit


####################################################################

#Seting up the GUI layout ##########################################
main_layout = [[main_menu_information_layer],
               [general_layer],
               [function_layer]]

chamber_layout = [[CTDI_information_layer],
                  [CTDI_layer, Couch_layer, CTDI_blade_layer],
                  [CTDI_run_layer]]

dicom_layout = [[dicom_information_layer], 
                [dicom_file_layer],
                [sg.Text('')],
                [dicom_patient_layer, dicom_planned_layer, dicom_graphics_layer]]


others_layout = [[settings_information_layout],
                 [ imaging_scan_layer, imaging_protocol_layer, History_layer],
                 [ Hidden_layer], 
                 ]

layout = [[ sg.Text('Monte Carlo - Dose Calculation for Risk Evaluation', justification='center', text_color='dark blue', font=('',40,'bold'))],
          [sg.TabGroup([[sg.Tab('Main menu' , main_layout),
                         sg.Tab('Simulation settings', others_layout),
                         sg.Tab('DICOM adjustments menu', dicom_layout, key= '-DICOM_TAB-', visible=False),
                         sg.Tab('CTDI phantom menu' , chamber_layout, key= '-CTDI_TAB-', visible=False),
                         ]],
                         key='-TAB GROUP-' ,expand_x=True, expand_y=True),
                        ]]

sg.set_options(scaling=1)
window = sg.Window(title= "MC-DCaRE", layout=layout, finalize=True, auto_size_text=True, font = ('', 15))

# Defining some required values
path = os.getcwd()
initiate = True
reset_tmp()
window["-G4FOLDERNAME-"].bind("<Return>","_ENTER") # for quick and dirty debuggin with G4 enter, remove for actual release

while True:
    event,values = window.read()

    if initiate == True: 
        # Sets up default values for resetting to default parameters
        values_default = values
        # Brute force work around as reseting all parameter will clear the default 'Browse' string on the buttons
        values_default['Browse'] =values_default['Browse0']=values_default['Browse1']=values_default['Browse2']= "Browse"
        initiate = False
    
    if event == '-RESET-':
        # HAS TO BE A LOOPED FUNCTION CAUSE PYSIMPLEGUI
        for i in values: 
            window[i].update(values_default[i])
        window['-CTDI_TAB-'].update(visible=False)
        window['-DICOM_TAB-'].update(visible=False)
        pass

    if event == '-G4FOLDERNAME-_ENTER':
        # THIS IS A PLACEHOLDER FOR QUICK AND DIRTY DEBUGGING

        # DUMP all values into a text file
        f = open('dump.txt', 'w')
        f.write( 'dict = '+repr(values)+ '\n')
        f.close()
        # imagemode = values['-DIRECTROT-'] +'_'+ values['-IMAGEMODE-']
        # print(imagemode)


    if event == '-FUNCTION_CHECK-':
        # Turns on or off visibility of the tab when checkbox is selected
        if values['-FUNCTION_CHECK-'] == 'DICOM':
            window['-DICOM_TAB-'].update(visible=True)
            window['-CTDI_TAB-'].update(visible=False)
        elif values['-FUNCTION_CHECK-'] == 'CTDI validation':
            window['-CTDI_TAB-'].update(visible=True)
            window['-DICOM_TAB-'].update(visible=False)
            
    if event == '-DICOM-':
        # Takes DICOM imageset location and checks it for CT images and pulls relevant data tags
        count_of_CT_images = 0
        count_of_RTPLAN = 0
        try:    
            DICOM_PATH = values['-DICOM-']
            list_of_files = os.listdir(DICOM_PATH)
            for files in list_of_files: 
                if  dcmread(os.path.join(DICOM_PATH,files)).Modality == 'CT':
                    if count_of_CT_images == 0:
                        count_of_CT_images += 1
                        patient_ID = dcmread(os.path.join(DICOM_PATH,files)).PatientID
                    elif count_of_CT_images != 0 : 
                        if dcmread(os.path.join(DICOM_PATH,files)).PatientID == patient_ID:
                            count_of_CT_images += 1
                        else:
                            raise 
            for files in list_of_files: 
                if dcmread(os.path.join(DICOM_PATH,files)).Modality == 'RTPLAN' and dcmread(os.path.join(DICOM_PATH,files)).PatientID == patient_ID:
                    if count_of_RTPLAN == 0:
                        count_of_RTPLAN += 1
                        isocentre_coors = dcmread(os.path.join(DICOM_PATH,files)).BeamSequence[0].ControlPointSequence[0].IsocenterPosition
                        values['-DICOM_ISOX-'] = str(round(isocentre_coors[0], 5)) + ' mm' 
                        values['-DICOM_ISOY-'] = str(round(isocentre_coors[1], 5)) + ' mm'
                        values['-DICOM_ISOZ-'] = str(round(isocentre_coors[2], 5)) + ' mm'
                        window['-DICOM_ISOX-'].update(values['-DICOM_ISOX-'])
                        window['-DICOM_ISOY-'].update(values['-DICOM_ISOY-'])
                        window['-DICOM_ISOZ-'].update(values['-DICOM_ISOZ-'])
                        values['-DICOMRP-'] = os.path.join(DICOM_PATH,files)
                        window['-DICOMRP-'].update(values['-DICOMRP-'])
                    elif count_of_RTPLAN != 0: 
                        if dcmread(os.path.join(DICOM_PATH,files)).PatientID == patient_ID:
                            count_of_RTPLAN += 1
                            sg.popup("More than 1 RTPlan found, please manually select one" , auto_close= True, non_blocking=True)
                            
            values['-PATID-'] = patient_ID
            window['-PATID-'].update(values['-PATID-'])
            sg.popup("Number of " + patient_ID + " CT images found" , count_of_CT_images , auto_close= True, non_blocking=True)
        except: 
            sg.popup_error("No CT images found in the folder or more than 1 patient file found")

    if event == '-DICOMRP-':
        # Takes DICOM RT plan and checks patientID match and pulls out isocentre data. 
        if dcmread(values['-DICOMRP-']).PatientID == values['-PATID-']: 
            try:    
                isocentre_coors = dcmread(values['-DICOMRP-']).BeamSequence[0].ControlPointSequence[0].IsocenterPosition
                values['-DICOM_ISOX-'] = str(round(isocentre_coors[0], 5)) + ' mm' #figure out how to get units form dicom 
                values['-DICOM_ISOY-'] = str(round(isocentre_coors[1], 5)) + ' mm'
                values['-DICOM_ISOZ-'] = str(round(isocentre_coors[2], 5)) + ' mm'
                window['-DICOM_ISOX-'].update(values['-DICOM_ISOX-'])
                window['-DICOM_ISOY-'].update(values['-DICOM_ISOY-'])
                window['-DICOM_ISOZ-'].update(values['-DICOM_ISOZ-'])
            except: 
                sg.popup_error("No isocentre found")
        else: 
            sg.popup_error('Patient ID for the CT image set and treatment plan does not match')        

    if event == '-DICOM_RUN-':
        # When users try to simulate DICOM imaging, this block will run. 
        # Code will activate the editor() function to edit the tmp file
        # Runtimehandler will then form the timestamp folder and drop the outputs there
        try: 
            tmp_headsource_file_path = path + '/tmp/headsourcecode.txt'
            editor(values, tmp_headsource_file_path, 'main')
            tmp_patient_file_path = path + '/tmp/patientDICOM.txt'
            editor(values, tmp_patient_file_path, 'sub')
            topas_application_path = values['-TOPAS-'] + " "
            float_anode_voltage, unit_anode_voltage = quantity_unit_stripper(values['-IMAGEVOLTAGE-'])
            float_exposure, unit_exposure = quantity_unit_stripper(values['-EXPOSURE-'])
            generate_new_topas_beam_profile(float_anode_voltage, float_exposure, values['-HIST-'], path)
            run_status = log_output(tmp_headsource_file_path, 'dicom', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)
        except:
            sg.popup_error("Ensure that you have specified a valid DICOM folder and file")
    
    if event == '-CTDI_RUN-':
        # When users try to simulate CTDI , this block will run. 
        # Code will activate the editor() function to edit the tmp file
        # Runtimehandler will then form the timestamp folder and drop the outputs there
        tmp_headsource_file_path = path + '/tmp/headsourcecode.txt'
        editor(values, tmp_headsource_file_path, 'main')
        topas_application_path = values['-TOPAS-'] + " "
        float_anode_voltage, unit_anode_voltage = quantity_unit_stripper(values['-IMAGEVOLTAGE-'])
        float_exposure, unit_exposure = quantity_unit_stripper(values['-EXPOSURE-'])
        generate_new_topas_beam_profile(float_anode_voltage, float_exposure, values['-HIST-'], path)

        if values['-CTDI_PHANTOM-'] == '16 cm': 
            tmp_16cm_file_path = path + '/tmp/CTDIphantom_16.txt'
            editor(values, tmp_16cm_file_path, 'sub')
            run_status = log_output(tmp_headsource_file_path, 'ctdi16', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)        
        elif values['-CTDI_PHANTOM-'] == '32 cm': 
            tmp_32cm_file_path = path + '/tmp/CTDIphantom_32.txt'
            editor(values, tmp_32cm_file_path, 'sub')
            run_status = log_output(tmp_headsource_file_path, 'ctdi32', topas_application_path, values['-FAN-'])
            reset_tmp()
            sg.popup(run_status)

    if event == '-IMAGEMODE-' or event == '-DIRECTROT-':
        # When users select the image protocol, this block will run and input the imaging parameteres
        # Hardcoded values for image protocol
        # Varian console shows scan field size. There the on screen value has to be converted to actaul blade position. 
        imagemode = values['-DIRECTROT-'] +'_'+ values['-IMAGEMODE-']
        rotrate, voltage , exposure, fan, timeend, NumofSeqence, NumofHistory, fieldx1, fieldx2, fieldy1, fieldy2, bladex1, bladex2, bladey1, bladey2 = imaging_modes_lookup[imagemode]
        # selection = ['Rotation Rate', 'kVp', 'exposure', 'Fan', 'BLADE_X1', 'BLADE_X2', 'BLADE_Y1', 'BLADE_Y2', 'FIELD_X1', 'FIELD_X2', 'FIELD_Y1', 'FIELD_Y2']
        values['-TIMEROTRATE-'] = rotrate
        values['-IMAGEVOLTAGE-'] = voltage
        values['-EXPOSURE-'] = exposure       
        values['-FAN-'] = fan
        values['-TIMELINEEND-'] = timeend
        values['-TIMESEQ-'] = NumofSeqence
        values['-HIST-'] = NumofHistory
        values['-FIELD_X1-'] = fieldx1
        values['-FIELD_X2-'] = fieldx2
        values['-FIELD_Y1-'] = fieldy1
        values['-FIELD_Y2-'] = fieldy2
        values['-BLADE_X1-'] = bladex1
        values['-BLADE_X2-'] = bladex2
        values['-BLADE_Y1-'] = bladey1
        values['-BLADE_Y2-'] = bladey2

        # values['-TIMEROTRATE-'], values['-IMAGEVOLTAGE-'], values['-EXPOSURE-'], values['-FAN-'], values['-TIMELINEEND-'] , values['-FIELD_X1-'], values['-FIELD_X2-'], values['-FIELD_Y1-'], values['-FIELD_Y2-'],a,b,c,d = imaging_modes_lookup[imagemode]

        window['-TIMEROTRATE-'].update(values['-TIMEROTRATE-'])
        window['-IMAGEVOLTAGE-'].update(values['-IMAGEVOLTAGE-'])
        window['-EXPOSURE-'].update(values['-EXPOSURE-'])
        window['-FAN-'].update(values['-FAN-'])
        window['-TIMELINEEND-'].update(values['-TIMELINEEND-'])
        window['-TIMESEQ-'].update(values['-TIMESEQ-'])
        window['-HIST-'].update(values['-HIST-'])
        window['-FIELD_X1-'].update(values['-FIELD_X1-'])
        window['-FIELD_X2-'].update(values['-FIELD_X2-'])
        window['-FIELD_Y1-'].update(values['-FIELD_Y1-'])
        window['-FIELD_Y2-'].update(values['-FIELD_Y2-'])
        window['-BLADE_X1-'].update(values['-BLADE_X1-'])
        window['-BLADE_X2-'].update(values['-BLADE_X2-'])
        window['-BLADE_Y1-'].update(values['-BLADE_Y1-'])
        window['-BLADE_Y2-'].update(values['-BLADE_Y2-'])

    if event == '-COUCH_TOG-':
        window['-COUCH-'].update(visible=values['-COUCH_TOG-'])

    if event == '-CTDI_BLADE_TOG-':
        window['-CTDI_BLADE-'].update(visible=values['-CTDI_BLADE_TOG-'])

    if event == sg.WIN_CLOSED:
        break

        
        

window.close()
