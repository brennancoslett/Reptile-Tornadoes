from framework import *
from tqdm import tqdm

def detectOnsets(input_dir, batch_size, pow, originSampleLen, minibatch = [0,1]):
    inputted_files = files_in_dir(input_dir)[minibatch[0]:minibatch[1]]
    frame_length = 0
    for i, file in tqdm(enumerate(inputted_files), desc="Detecting Onsets",
                    total=len(inputted_files)):
        frame_energies, frame_length = calcFrameEnergies(file)
        #print(str(frame_energies[0:100].std()**.5) + " " + str(frame_energies[0:150].std()**.5))
        file_pp_min =  (frame_energies[:originSampleLen].mean() + frame_energies[:originSampleLen].std()) / 2 ** pow
        # calculate peaks
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

