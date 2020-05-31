from framework import *

def onsetDetector(inputted_files):
    for i,file in enumerate(inputted_files):
        frame_energies, frame_length = calcFrameEnergies(file)

        # plot frame energies over time
        plt.plot(frame_energies)
        plt.title(f'{file.name} Frames: {frame_energies.size}')
        plt.show()
        #print(i)

onsetDetector(import_dir(r"C:\Users\brenn\iCloudDrive\College\Y2S2\Classes\0 Audio Processing\REPO\Reptile-Tornadoes\Training Data\train\train"))
    

