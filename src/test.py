import os
import stft
import numpy as np
import scipy.io.wavfile as wav
from framework import *

def autoCorrelation(signal):
    sigSize = signal.size
    norm = (signal - np.mean(signal))
    res = np.correlate(norm, norm, mode='same')
    aCorr = res[sigSize//2 + 1:] / (signal.var() * np.arange(sigSize-1, sigSize//2, -1))
    lag = np.abs(aCorr).argmax() + 1
    r = aCorr[lag-1]
    if np.abs(r) > 0.5:
        print('Autocorrelated with r = {}, lag = {}'. format(r, lag))
    else:
        print('Not autocorrelated')
    # i think the training data is 60 - 120 bpm????????
    # bpm60 = r*60/lag
    # bpm120 = r*120/lag
    # bpm = []
    # bpm = 60 /lag
    # bpm[1] = r*120/lag

    return aCorr, r, lag
    # Note to self: look up more about scipy.​signal.​signaltools.correlate
rand1 = np.random.randint(7, size=3)
rand2 = np.random.randint(7, size=2)
s1 = np.array([7,5,rand2[0],6,1,rand2[1],5,6,3,rand1[0],rand1[1],rand1[2]] * 20)
aCorr, r, lag = autoCorrelation(s1)
print(r)
print(lag)
print(aCorr)
# print(bpm)
print("-"*20)
s2 = np.random.randint(7, size=1000)
aCorr, r, lag = autoCorrelation(s2)
# str(bpm)
print(r)
print(lag)
# print(aCorr)
# print(bpm)
# print("bmp120:" bpm)
print("-"*20)

# sample_rate, samples = wav.read('C:\SchoolJKU\Audio\Reptile-Tornadoes\Training Data\train\ff123_2nd_vent_clip.wav')
# s3 = stft.spectrogram(samples,framelength=2*1024, hopsize=1024)
# # s3, s3Lenght = wavToSTFT("C:\SchoolJKU\Audio\Reptile-Tornadoes\Training Data\train\ff123_2nd_vent_clip.wav")
# aCorr, r, lag = autoCorrelation(s3)
# print(r)
# print(lag)
# print(aCorr)