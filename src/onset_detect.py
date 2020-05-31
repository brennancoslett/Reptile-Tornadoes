from framework import *

def onsetDetector(input_dir):
    inputted_files = import_dir(input_dir)
    frame_length = 0
    for file in inputted_files:
        frame_energies, frame_length = calcFrameEnergies(file)
        #print(str(frame_energies[0:100].std()**.5) + " " + str(frame_energies[0:150].std()**.5))
        file_pp_min =  frame_energies[:100].std()
        # calculate peaks
        batch_size = 5
        filePeaks = []
        for value in range(batch_size, frame_energies.size,batch_size):
            localMax = np.argmax(frame_energies[value - batch_size:value])
            try:
                if (frame_energies[localMax + value] > file_pp_min):
                    if np.isin(localMax+ value, filePeaks, invert=True):    
                        filePeaks.append(localMax + value)
            except:
                pass
            
        #log to file
        logfile = Path.joinpath(Path(input_dir),file.stem + ".onsets.pr")
        with logfile.open("w+") as f:
            for peak in filePeaks:
                f.write(f'{(peak * frame_length):0.9f}\n')
        print(logfile.name + " Created")
                
    

onsetDetector(r"C:\Users\brenn\iCloudDrive\College\Y2S2\Classes\0 Audio Processing\REPO\Reptile-Tornadoes\Training Data\train\train")
    

