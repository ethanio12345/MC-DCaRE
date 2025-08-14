import spekpy as sp
import numpy as np
import matplotlib.pyplot as plt

def generate_new_topas_beam_profile(anode_voltage:float, exposure:float, Histories:str, path):
    s=sp.Spek(kvp=anode_voltage,th=14,mas =exposure,dk = 0.2, z=0.1,
              ) # unfiltered spectrum at 1mm 
    s.filter('Al',2.7) #2.7mm filter at the kV xray tube exit window from manual
    
    summary_of_inputs = s.state.get_current_state_str('full', s.get_std_results())
    # Export (save) spectrum to file, doesnt seem to be used
    # s.export_spectrum('imaging_params.spk', comment='for topas export')
    # by default, diff is true but if not true, means fluence is given per bin (with width) instead of per energy (keV)
    # which results in sum(spkarr) = 2* s.get_flu. reason unknown. if diff set to true (use fluence in bin instead of 
    # per energy in keV)
    # this does not change the spectrum dynamic- only scale it across the whole spectrum by 0.5
    karr, spkarr = s.get_spectrum(edges= False, diff = False) # returns an array of photon energies and its corresponding fluence
    no_particles = 4*np.pi*0.1**2*s.get_flu()
    
    #multiply dose by this factor to get absolute dose - since reduce the numberhistories to 2009895
    calib_factor = no_particles/int(Histories) # no_particles/Histories
    with open(path + '/tmp/head_calibration_factor.txt', 'w') as f:
        f.write('%d' % calib_factor)
        f.write('\nMultiply dose by the factor above to get absolute dose \n')
        f.write('The number of histories in this run was: ' + Histories+'\n')
        f.write('Calibration factor = Number of particles/Histories\n')
        f.write('\n')
        f.write(summary_of_inputs)

    #normalising fluence by the total fluence to get weights for each energy bin 
    normalised_spec = spkarr/s.get_flu()
    #check that all weights sum up close to one
    # print(sum(normalised_spec))

    normalised_spec_trimmed = []
    for i in normalised_spec:
        if i >0.000001:
            #normalised_spec_trimmed.append(float(format(i, '.6f')))
            normalised_spec_trimmed.append(float(format(i, '.6f')))
        else:
            normalised_spec_trimmed.append(0)

    np.set_printoptions(suppress=True) #suppress removes scientific notation
    weightedFluence = np.asarray(normalised_spec_trimmed)
    weightedFluence = np.insert(weightedFluence, 0, weightedFluence.size)
    energySpectrum = np.insert(karr, 0, karr.size)
    energySpectrum = np.delete(energySpectrum, 0)
    weightedFluence = np.delete(weightedFluence, 0)
    convertedFile = "dv:So/beam/BeamEnergySpectrumValues = " + str(energySpectrum.size) + "\n " \
                    + str(energySpectrum)[1:-1] + " keV \n" \
                    + "\n uv:So/beam/BeamEnergySpectrumWeights = " + str(weightedFluence.size) + "\n "\
                    + str(weightedFluence)[1:-1]


    with open(path +'/tmp/ConvertedTopasFile.txt', 'w') as f:
        f.write(convertedFile)
        # ...

def parse_topas_file(filepath):
    """Parse the TOPAS energy spectrum file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by the TOPAS parameter markers
    parts = content.split('dv:So/beam/BeamEnergySpectrumValues = 620')
    if len(parts) < 2:
        raise ValueError("Could not find energy values in file")
    
    energy_part = parts[1].split('uv:So/beam/BeamEnergySpectrumWeights = 620')[0]
    weight_part = parts[1].split('uv:So/beam/BeamEnergySpectrumWeights = 620')[1]
    
    # Parse energy values - handle 'keV' suffix
    energy_str = energy_part.replace('\n', ' ').strip()
    energy_tokens = [x.replace('keV', '') for x in energy_str.split() if x.strip()]
    energies = [float(x) for x in energy_tokens if x]
    
    # Parse weight values
    weight_str = weight_part.replace('\n', ' ').strip()
    weight_tokens = [x for x in weight_str.split() if x.strip()]
    weights = [float(x) for x in weight_tokens if x]
    
    return np.array(energies), np.array(weights)

def plot_spectrum(energies, weights, output_file='spectrum_plot.png'):
    """Plot the energy spectrum."""
    plt.figure(figsize=(12, 8))
    
    # Create the plot
    plt.subplot(2, 1, 1)
    plt.plot(energies, weights, 'b-', linewidth=1.5)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Weight')
    plt.title('TOPAS Beam Energy Spectrum')
    plt.grid(True, alpha=0.3)
    
    # Log scale plot for better visibility of small values
    plt.subplot(2, 1, 2)
    plt.semilogy(energies, weights, 'r-', linewidth=1.5)
    plt.xlabel('Energy (keV)')
    plt.ylabel('Weight (log scale)')
    plt.title('TOPAS Beam Energy Spectrum (Log Scale)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print some statistics
    print(f"Energy range: {energies.min():.1f} - {energies.max():.1f} keV")
    print(f"Total weight: {np.sum(weights):.6f}")
    print(f"Peak weight: {np.max(weights):.6f} at {energies[np.argmax(weights)]:.1f} keV")
    
    
if __name__ == '__main__' : 
    # input values
    anode_voltage = 125 #'100 kV'
    exposure = 10 #'100 mAs'
    Histories = "100"
    generate_new_topas_beam_profile(anode_voltage, exposure, Histories, '/home/bchcphysics/Applications/MC-DCaRE')
    filepath = '/home/bchcphysics/Applications/MC-DCaRE/tmp/ConvertedTopasFile.txt'
    energies, weights = parse_topas_file(filepath)
    plot_spectrum(energies, weights)



