# Helper script to set up the GUI elements. Edits to elements should be made here. Another daughter script called defaultvalues.py is used to store all the default parameters. 
import FreeSimpleGUI as sg
sg.theme('Reddit')
from src.defaultvalues import *

general_layer = sg.Frame('General Settings',
                [ 
                  [sg.Text('G4 Data Directory',size = (17,1), text_color='black'),
                    sg.In(default_text=default_G4_Directory,key='-G4FOLDERNAME-',size=(50,1),enable_events=True),sg.FolderBrowse(button_text= "Browse", key= 'Browse' )],
                  [sg.Text('TOPAS Directory',size =(17,1),text_color='black'),
                    sg.In(default_text=default_TOPAS_Directory,key='-TOPAS-',size=(50,1),enable_events=True),sg.FileBrowse(button_text= "Browse", key= 'Browse0')],
                  [sg.Button(button_text='Reset all parameters to default', key='-RESET-')],
              ])

main_menu_information_layer = sg.Frame('Instructions on the usage of the GUI', 
                             [ 
                               [sg.Text('Select your Topas and G4 data directories. Next, select the function you would like to enable. ')],
                               [sg.Text('   DICOM allows the user to specify a patient DICOM CT image folder to run simulations on')],
                               [sg.Text('   CTDI validation is for running simulations on CTDI phantom')],
                               [sg.Text('In the following pages, type in your desired value, a whitespace followed by the unit. Eg. 5 mm')],
                               [sg.Text('XYZ corresponds to patient coordinate system; Left = +X, Posterior = +Y, Head = +Z')],
                               [sg.Text('The scan angle is defined from the kV imaging source, if the kV source in on top of the patient, this is 0 degrees')],
                             ]) 

function_layer = sg.Frame('Choose your function',
                          [
                            [sg.Text('Simulation type',size = (20,1),  text_color='black'),
                             sg.Combo(['DICOM', 'CTDI validation'], default_value=None , key='-FUNCTION_CHECK-', readonly=True, enable_events=True, size = 20 )],
                          ])

settings_information_layout = sg.Frame("General settings", 
                           [
                               [sg.Text('This page contains general settings used for all simulations.')],
                               [sg.Text('You will be able to control the granularity of the simulations along with the scan parameters here.')],
                               [sg.Text('To use kV-kV option, the user will have to manually input the desired angle.')],
                               [sg.Text('For 2 or more kV-kV angles, please run the indivual angles separately.')],
                               [sg.Text('It is a known issue where using more threads than what your computer can support will result in the simulation failing.')],

                           ])           

Hidden_layer = sg.Frame("Time Feature and other hidden values",
                [   
                    [sg.Text('Verbosity',size = (14,1), text_color='black'),
                     sg.In(default_text=default_TIME_VERBOSITY,key='-TIMEVERBO-',size=(10,1),  enable_events=True)],
                    [sg.Text('Timeline End',size = (14,1), text_color='black'),
                     sg.In(default_text=default_TIME_TIME_END,key='-TIMELINEEND-',size=(10,1),  enable_events=True)],
                    [sg.Text('Rotate Rate',size = (14,1), text_color='black'),
                    sg.In(default_text=default_TIME_ROT_RATE,key='-TIMEROTRATE-',size=(15,1),  enable_events=True, readonly=True)],
                    [sg.In(default_text= default_BLADE_X1, key = '-BLADE_X1-',size = (10,1), text_color='black', enable_events=True, readonly=True)],
                    [sg.In(default_text= default_BLADE_X2, key = '-BLADE_X2-',size = (10,1), text_color='black', enable_events=True, readonly=True)],
                    [sg.In(default_text= default_BLADE_Y1, key = '-BLADE_Y1-',size = (10,1), text_color='black', enable_events=True, readonly=True)],
                    [sg.In(default_text= default_BLADE_Y2, key = '-BLADE_Y2-',size = (10,1), text_color='black', enable_events=True, readonly=True)],
                ], visible=False)

History_layer = sg.Frame("Simulation settings",
                [
                  [sg.Text('Seed',size =(10,1),text_color='black'),
                   sg.In(default_text=default_Seed,key='-SEED-',size=(10,1),enable_events=True)],
                  [sg.Text('Threads',size = (10,1),text_color='black'),
                   sg.In(default_text=default_Threads,key='-THREAD-',size=(10,1),enable_events=True)],
                  [sg.Text('Seq Time',size = (10,1), text_color='black'),
                    sg.In(default_text=default_TIME_SEQ_TIME,key='-TIMESEQ-',size=(10,1),  enable_events=True, readonly=True)],
                  [sg.Text('Histories',size = (10,1),text_color='black'),
                   sg.In(default_text=default_Histories,key='-HIST-',size=(10,1),enable_events=True)],
                ], vertical_alignment='top')

imaging_protocol_layer = sg.Frame('Imaging protocol',
                      [ [sg.Text('Imaging mode',size = (10,1), text_color='black'),
                         sg.Combo(['Image Gently', 'Head', 'Short Thorax', 'Spotlight', 'Thorax', 'Pelvis', 'Pelvis Large'],default_value='Image Gently', key='-IMAGEMODE-', readonly=True ,enable_events=True)],
                        [sg.Text('Fan mode',size = (10,1), text_color='black'),
                         sg.In(default_text=default_FAN_MODE, key='-FAN-',size = (15,1), text_color='black', enable_events=True,  readonly=True )],
                        [sg.Text('Blade X1', size = (10,1), text_color='black'),
                         sg.In(default_text= default_FIELD_X1, key = '-FIELD_X1-',size = (15,1), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Blade X2', size = (10,1), text_color='black'),
                         sg.In(default_text= default_FIELD_X2, key = '-FIELD_X2-',size = (15,1), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Blade Y1', size = (10,1), text_color='black'),
                         sg.In(default_text= default_FIELD_Y1, key = '-FIELD_Y1-',size = (15,1), text_color='black', enable_events=True, readonly=True)],
                        [sg.Text('Blade Y2', size = (10,1), text_color='black'),
                         sg.In(default_text= default_FIELD_Y2, key = '-FIELD_Y2-',size = (15,1), text_color='black', enable_events=True, readonly=True)],
                      ])

imaging_scan_layer = sg.Frame('Set up imaging parameters', 
                      [ [sg.Text('Start angle',size = (12,1), text_color='black'),
                         sg.In(default_text=default_IMAGE_START_ANGLE,key='-STARTANGLEROT-',size=(15,1),  enable_events=True)],
                        [sg.Text('CBCT or kV-kV',size = (12,1), text_color='black'),
                         sg.Combo(['CBCT Clockwise', 'CBCT Anticlockwise', 'kV-kV'], default_value='CBCT Clockwise' ,key='-DIRECTROT-', readonly=True ,enable_events=True, size=(15,1))],
                        [sg.Text('kVp',size = (12,1), text_color='black'),
                        sg.In(default_text=default_IMAGE_VOLTAGE,key='-IMAGEVOLTAGE-',size=(15,1),  enable_events=True)], 
                        [sg.Text('Exposure',size = (12,1), text_color='black'),
                        sg.In(default_text=default_EXPOSURE,key='-EXPOSURE-',size=(15,1),  enable_events=True)]
                        ], vertical_alignment='top')

dicom_information_layer = sg.Frame('Instructions on the usage of the DICOM adjustments', 
                             [ 
                               [sg.Text('The programme automatically shifts the patient such that the isocentre of the treatment plan is matched to the isocentre of the beam.')],
                               [sg.Text('For patient set up adjustments, make any adjustments relative to the ioscentre of the treatment plan.')],
                               [sg.Text('If the first imaging scan was Left, Posterior and Superior of the planned isocentre, this would be a positve XYZ input.')],
                               [sg.Text('Use the previous tab to make edits to other parameters like collimator openings and exposure. ')],
                               [sg.Text('The programme currently only supports CT modality.')],
                             ]) 

dicom_file_layer = sg.Frame("DICOM inputs",
                              [ 
                                [sg.Text('DICOM Directory',size =(17,1),text_color='black'),
                                 sg.In(default_text=default_DICOM_Directory,key='-DICOM-',size=(50,1),enable_events=True),sg.FolderBrowse(button_text= "Browse", key= 'Browse1' )
                                ],
                                [sg.Text('Loaded patient ID:',size =(17,1),text_color='black'),
                                 sg.In(default_text = '', key = '-PATID-' ,size =(17,1),text_color='black', background_color='light grey', enable_events=True, readonly= True)],
                                [sg.Text('DICOM RP file',size =(17,1),text_color='black'),
                                 sg.In(default_text=default_DICOM_RP_file,key='-DICOMRP-',size=(50,1),enable_events=True),sg.FileBrowse(button_text= "Browse", key= 'Browse2' ,file_types= (("DICOM File",'*.dcm'),) )
                                ],
                                [sg.Text('File output name',size =(17,1),text_color='black'),
                                 sg.In(default_text=default_DICOM_Output_File_Name,key='-DICOM_OUTPUT_NAME-',size=(50,1),enable_events=True),
                                 sg.Checkbox('Use default', enable_events=True, key='-DICOM_OUTPUT_NAME_TOG-', default= True)
                                ],
                                [sg.Button("Run set up imaging dose simulation",enable_events=True, key='-DICOM_RUN-',size=(35,1))],
                              ])

dicom_patient_layer = sg.Frame('Patient set up adjustments',
                    [
                        [sg.Text('X shift from iso',size = (14,1), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_X,key='-DICOM_TX-',size=(10,1),  enable_events=True)],
                        [sg.Text('Y shift from iso',size = (14,1), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_Y,key='-DICOM_TY-',size=(10,1),  enable_events=True)],
                        [sg.Text('Z shift from iso',size = (14,1), text_color='black'),
                        sg.In(default_text=default_DICOM_TRANS_Z,key='-DICOM_TZ-',size=(10,1),  enable_events=True)],
                        [sg.Text('Yaw',size = (14,1), text_color='black'),
                        sg.In(default_text=default_DICOM_ROT_Z,key='-DICOM_YAW-',size=(10,1),  enable_events=True)], 
                    ])


dicom_planned_layer = sg.Frame('Treatment plan parameters',
                    [
                        [sg.Text('Isocenter X',size = (10,1), text_color='black'),
                        sg.In(default_text= default_DICOM_ISOCENTER_X, key='-DICOM_ISOX-',size=(10,1),  enable_events=True, readonly=True)],
                        [sg.Text('Isocenter Y',size = (10,1), text_color='black'),
                        sg.In(default_text=default_DICOM_ISOCENTER_Y, key='-DICOM_ISOY-',size=(10,1),  enable_events=True, readonly=True)],
                        [sg.Text('Isocenter Z',size = (10,1), text_color='black'),
                        sg.In(default_text=default_DICOM_ISOCENTER_Z, key='-DICOM_ISOZ-',size=(10,1),  enable_events=True, readonly=True)],
                    ], vertical_alignment='top')

dicom_graphics_layer = sg.Frame('DICOM simulation graphics',
                               [[sg.Checkbox("DICOM graphics toggle", enable_events=True, key='-DICOM_GRAPHICS-', default= False)],
                                [sg.Text('It is highly recommended to never use this ')],
                                [sg.Text('due to excessive lag from the large image set. ')],
                                ], vertical_alignment='top')


CTDI_information_layer = sg.Frame('Instructions on the usage of the CTDI phantom parameters', 
                             [ 
                               [sg.Text('Select the CTDI phantom used for the CTDI validation. The phantom will be automatically centered at isocenter.')],
                               [sg.Text('Simulation will automatically generate and run 5 CTDI simulations for all 5 possible detector position.')],
                               [sg.Text('Use the previous tab to make edits to other parameters like collimator openings and exposure. ')],
                               [sg.Text('Use the couch toggle to select or remove the couch from the simulation, depending on your set up')],
                               [sg.Text('The phantom is automatically placed on top of the couch if the couch is selected.')],
                               [sg.Text('You can also choose to change the thickeness of the couch in terms of its aluminium thickness.')]
                             ]) 

CTDI_layer = sg.Frame('CTDI options',
                    [
                      [sg.Text('CTDI phantom used',size = (25,1), text_color='black'),
                       sg.Combo(['16 cm', '32 cm'], default_value='16 cm' ,key='-CTDI_PHANTOM-', readonly=True )],
                      [sg.Text('Dose to medium Zbins',size = (25,1), text_color='black'),
                      sg.In(default_text=default_DTM_Zbins,key='-DTMZB-',size=(10,1),  enable_events=True)],
                      [sg.Text('Track Length Estimator Zbins',size = (25,1), text_color='black'),
                      sg.In(default_text=default_TLE_Zbins,key='-TLEZB-',size=(10,1),  enable_events=True)],
                      [sg.Text('Dose to water Zbins',size = (25,1), text_color='black'),
                      sg.In(default_text=default_DTW_Zbins,key='-DTWZB-',size=(10,1),  enable_events=True)],
                      [sg.Checkbox("Couch toggle",  enable_events=True, key='-COUCH_TOG-', default= True)],
                      [sg.Checkbox("CTDI user blade toggle (Defaults to imaging settings)",  enable_events=True, key='-CTDI_BLADE_TOG-', default= False)],
                    ], vertical_alignment='top')

Couch_layer = sg.pin(sg.Frame("Couch",
                [
                   [sg.Text('Length',size = (8,1), text_color='black'),
                     sg.In(default_text=default_COUCH_HLZ,key='-COUCHHLZ-',size=(10,1),  enable_events=True)],
                   [sg.Text('Width',size = (8,1), text_color='black'),
                     sg.In(default_text=default_COUCH_HLX,key='-COUCHHLX-',size=(10,1),  enable_events=True)],
                   [sg.Text('Thickness',size = (8,1), text_color='black'),
                     sg.In(default_text=default_COUCH_HLY,key='-COUCHHLY-',size=(10,1),  enable_events=True)],
                ], key='-COUCH-', visible= True, vertical_alignment='top' ), shrink=False, vertical_alignment='top' )

CTDI_blade_layer = sg.pin(sg.Frame("CTDI user specified jaw",
                [
                  [sg.Text('Blade X1', size = (10,1), text_color='black'),
                    sg.In(default_text= default_FIELD_X1, key = '-CTDI_FIELD_X1-',size = (15,1), text_color='black', enable_events=True)],
                  [sg.Text('Blade X2', size = (10,1), text_color='black'),
                    sg.In(default_text= default_FIELD_X2, key = '-CTDI_FIELD_X2-',size = (15,1), text_color='black', enable_events=True)],
                  [sg.Text('Blade Y1', size = (10,1), text_color='black'),
                    sg.In(default_text= default_FIELD_Y1, key = '-CTDI_FIELD_Y1-',size = (15,1), text_color='black', enable_events=True)],
                  [sg.Text('Blade Y2', size = (10,1), text_color='black'),
                    sg.In(default_text= default_FIELD_Y2, key = '-CTDI_FIELD_Y2-',size = (15,1), text_color='black', enable_events=True)],
                ], key='-CTDI_BLADE-', visible= False, vertical_alignment='top' ), shrink=False, vertical_alignment='top' )

CTDI_run_layer= sg.Frame('Activate CTDI simulation', 
                           [
                             [sg.Checkbox("CTDI graphics toggle", enable_events=True, key='-CTDI_GRAPHICS-', default= False)],
                             [sg.Button("Run", enable_events=True, key='-CTDI_RUN-', disabled=False, disabled_button_color='grey')],
                            ])
     