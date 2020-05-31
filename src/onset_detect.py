from framework import *

def onsetDetector(inputted_files):
    for i,file in enumerate(inputted_files):
        frame_energies = calcFrameEnergies(file)
        # https://stackoverflow.com/questions/41576536/normalizing-complex-values-in-numpy-python
        frame_energies_norm = frame_energies - frame_energies.real.min() - 1j*frame_energies.imag.min() 
        frame_energies_norm = (frame_energies_norm/np.abs(frame_energies).max()).real
        
        # plot frame energies over time
        plt.plot(frame_energies_norm)
        plt.title(f'{file.name} Frames: {frame_energies.size}')
        plt.show()
        #print(i)

onsetDetector(import_dir(r"C:\Users\brenn\iCloudDrive\College\Y2S2\Classes\0 Audio Processing\REPO\Reptile-Tornadoes\Training Data\train\train"))
    

