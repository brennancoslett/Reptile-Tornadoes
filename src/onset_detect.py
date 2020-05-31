from framework import *

def onsetDetector(input_dir):
    inputted_files = import_dir(input_dir)
    frame_length = 0
    for i,file in enumerate(inputted_files):
        frame_energies, frame_length = calcFrameEnergies(file)
        file_pp_min =  frame_energies[:100].std()
        # plot frame energies over time
        # plt.plot(frame_energies)
        # plt.title(f'{file.name} Frames: {frame_energies.size}')
        # plt.show()
        # calculate peaks
        filePeaks = []
        for value in range(5, frame_energies.size,5):
            localMax = np.argmax(frame_energies[value - 5:value])
            try:
                if (frame_energies[localMax + value] > file_pp_min):
                    if np.isin(localMax+ value, filePeaks, invert=True):    
                        filePeaks.append(localMax + value)
            except:
                pass
            
        #log to file
        logfile = Path.joinpath(Path(input_dir),'pr',file.stem + ".onsets.pr")
        with logfile.open("w+") as f:
            for peak in filePeaks:
                f.write(f'{(peak * frame_length):0.9f}\n')
        print(str(logfile) + "created")
                
    

onsetDetector(r"C:\Users\brenn\iCloudDrive\College\Y2S2\Classes\0 Audio Processing\REPO\Reptile-Tornadoes\Training Data\train\train")
    

