import os
import stft
import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path
from matplotlib import pyplot as plt

defaultTol = 0.1

def files_in_dir(input_dir, file_type = "*.wav"):
    #pulls file paths from input directory
    input_dir = Path(os.path.abspath(input_dir))
    inputted_files = sorted(input_dir.rglob(file_type))   
    return inputted_files

def importListFromFile(file_path: Path):
    listFromFile = []
    with file_path.open('r') as f:
        for line in f:
            listFromFile.append(float(line))
    return listFromFile

def clearExcess(valueList, tolerance):
    newValueList = []
    for i in range(1, len(valueList)):
        if valueList[i] - valueList[i-1] > tolerance:
            newValueList.append(valueList[i-1])
    return newValueList
    
def wavToSTFT(file):
        fs, audio = wav.read(str(file))
        STFT = stft.spectrogram(audio)
        frameLength = (audio.size/fs)/STFT.shape[1]
        return STFT, frameLength
    
def calcFrameEnergies(file_path):
        file_stft, frameLength = wavToSTFT(file_path)
        numFrames = file_stft.shape[1]
        numBins = file_stft.shape[0]
        frame_energies = np.zeros(numFrames, dtype='complex128')
        for j, Bin in enumerate(file_stft):
            for k, Frame in enumerate(Bin):
                frame_energies[k] += (abs(np.sqrt(Frame**2))) * (float((((.5*numBins)-j))) / (.5*numBins))**(-2.5)
        # https://stackoverflow.com/questions/41576536/normalizing-complex-values-in-numpy-python
        frame_energies_norm = frame_energies - frame_energies.real.min() - 1j*frame_energies.imag.min() 
        frame_energies_norm = (frame_energies_norm/np.abs(frame_energies).max()).real
        return frame_energies_norm, frameLength

def evalFunc(predictFilePathList, gtFilePathList, tolerance = defaultTol):
    for i, file in enumerate(predictFilePathList):
        evalValues = []
        prValues = clearExcess(importListFromFile(file), tolerance)
        gtValues = importListFromFile(gtFilePathList[i])
        
        tp = 0
        fp = 0
        fn = 0
        truthCursor = 0
        predictCursor = 0
        cumError = 0.0
        
        while(truthCursor < len(gtValues) and predictCursor < len(prValues)):
            trueEvent = gtValues[truthCursor]
            predictEvent = prValues[predictCursor]
            error = abs(trueEvent - predictEvent)
            
            if error < tolerance:
                tp += 1
                truthCursor += 1
                predictCursor += 1
                cumError += error
            elif predictEvent < trueEvent:
                fp+= 1
                predictCursor += 1
            elif predictEvent > trueEvent:
                fn += 1
                truthCursor += 1
            else:
                raise RuntimeError(f"Cannot match gt {trueEvent} with prediction {predictEvent}")
            
        fn = fn + (len(gtValues) - truthCursor)
        fp = fp + (len(prValues) - predictCursor)   
        cumError *= 1e6
        evalValues.append([cumError, tp, fp, fn, file.name])
        
    avgCumError = 0
    avgTp = 0 
    avgFp = 0
    avgFn = 0
    
    for subarray in evalValues:
       avgCumError += subarray[0]
       avgTp += subarray[1]
       avgFp += subarray[2]
       avgFn += subarray[3]
    percentTrue = avgTp /(avgTp + avgFp + avgFn)
    avgEvalValues = np.array([avgCumError,avgTp, avgFp, avgFn]) / len(evalValues)
    return [percentTrue, avgEvalValues, evalValues]  