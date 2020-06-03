import os
import stft
import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path
from matplotlib import pyplot as plt

defaultTol = 0.1

def files_in_dir(input_dir, file_type = "*.wav"):
    '''
    iterates through a directory and creates a list of pathlib Paths\n
    file_type: defaults to ".wav", can be changed to any str\n
    inputted_files: list of all files in directory with type file_type\n
    return inputted_files
    '''
    input_dir = Path(os.path.abspath(input_dir))
    inputted_files = sorted(input_dir.rglob(file_type))   
    return inputted_files

def importListFromFile(file_path: Path):
    '''
    iterates through all lines in file to create a list of values
    '''
    listFromFile = []
    with file_path.open('r') as f:
        for line in f:
            listFromFile.append(float(line))
    return listFromFile

def clearExcess(valueList, tolerance):
    '''
    removes all values in valueList that are within tolerance.
    '''
    newValueList = []
    for i in range(1, len(valueList)):
        if valueList[i] - valueList[i-1] > tolerance:
            newValueList.append(valueList[i-1])
    return newValueList
    
def wavToSTFT(file: Path):
    '''
    converts .wav file to STFT\n
    file: pathlib Path to wav file\n
    return STFT, frameLength
    '''
    fs, audio = wav.read(str(file))
    STFT = stft.spectrogram(audio, hopsize= 512, padding= 2)
    frameLength = (audio.size/fs)/STFT.shape[1]
    return STFT, frameLength
    
def calcFrameEnergies(file_path: Path, weightForHFC = False):
    '''
    calcFrameEnergies takes path to a .wav file, calculates the STFT
    and creates an array frame_energies[] with the cumulative energy at each frame in the STFT.\n
    @weightForHFC: defaults to False, \nwhen enabled weights the energy in each bin with High Frequency Content given highest weight\n
    return: frameEnergiesNorm, frameLength 
    '''
    file_stft, frameLength = wavToSTFT(file_path)
    numFrames = file_stft.shape[1]
    numBins = file_stft.shape[0]
    frame_energies = np.zeros(numFrames, dtype='complex128')
    if weightForHFC:
        for j, Bin in enumerate(file_stft):
            for k, Frame in enumerate(Bin):
                frame_energies[k] += abs(np.sqrt(Frame*2)) * (1.5*j/numBins) * ((np.exp(j/numBins)-1)/(np.exp(1)-1))
    else:
        for j, Bin in enumerate(file_stft):
            for k, Frame in enumerate(Bin):
                frame_energies[k] += abs(np.sqrt(Frame*2))
    # https://stackoverflow.com/questions/41576536/normalizing-complex-values-in-numpy-python
    frameEnergiesNorm = frame_energies - frame_energies.real.min() - 1j*frame_energies.imag.min() 
    frameEnergiesNorm = (frameEnergiesNorm/np.abs(frame_energies).max()).real
    return frameEnergiesNorm, frameLength

def evalFunc(predictFilePathList, gtFilePathList, tolerance = defaultTol):
    '''
    takes filePath lists for predictions and groundtruths and evaluates the num of TruePositives, FalsePositives, and FalseNegatives.\n
    return: [F_measure, P_R_return, evalValues]\n
    F_measure: calculated F Measure over entire evaluated set\n
    P_R_return: values for Precision and Recall used to calc F_measure\n
    evalValues: [cumError, tp, fp, fn, file.name]
    '''
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
       
    precision = avgTp/(avgTp + avgFp)
    recall = avgTp/(avgTp + avgFn)
    F_measure = 2*((precision* recall)/(precision + recall))
    
    avgCumError /= len(evalValues)
    avgTp /= len(evalValues)
    avgFp /= len(evalValues)
    avgFn /= len(evalValues)
    
    P_R_return = [precision, recall]
    return [F_measure, P_R_return, evalValues]  