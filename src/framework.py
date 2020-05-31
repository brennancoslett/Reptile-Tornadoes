import os
import stft
import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path
from matplotlib import pyplot as plt

def import_dir(input_dir):
    #pulls file paths from input directory
    input_dir = Path(os.path.abspath(input_dir))
    inputted_files = sorted(input_dir.rglob("*.wav"))   
    return inputted_files

def calcFrameEnergies(file):
        fs, audio = wav.read(str(file))
        file_stft = stft.spectrogram(audio)#, padding = 1)
        numFrames = file_stft.shape[1]
        numBins = file_stft.shape[0]
        frame_energies = np.zeros(numFrames, dtype='complex128')
        for j, Bin in enumerate(file_stft):
            for k, Frame in enumerate(Bin):
                frame_energies[k] += (abs(Frame.real)**2) * (float((((.5*numBins)-j))) / (.5*numBins))**(-2.5)
        return frame_energies