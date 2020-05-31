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

def wavToSTFT(file):
        fs, audio = wav.read(str(file))
        STFT = stft.spectrogram(audio)
        frameLength = (audio.size/fs)/STFT.shape[1]
        return STFT, frameLength
    
def calcFrameEnergies(file_path):
        file_stft, frameLenth = wavToSTFT(file_path)
        numFrames = file_stft.shape[1]
        numBins = file_stft.shape[0]
        frame_energies = np.zeros(numFrames, dtype='complex128')
        for j, Bin in enumerate(file_stft):
            for k, Frame in enumerate(Bin):
                frame_energies[k] += (abs(Frame.real)**2) * (float((((.5*numBins)-j))) / (.5*numBins))**(-2.5)
                # https://stackoverflow.com/questions/41576536/normalizing-complex-values-in-numpy-python
        frame_energies_norm = frame_energies - frame_energies.real.min() - 1j*frame_energies.imag.min() 
        frame_energies_norm = (frame_energies_norm/np.abs(frame_energies).max()).real
        return frame_energies_norm, frameLength