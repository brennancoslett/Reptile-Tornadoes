from framework import *
import shutil
from tqdm import tqdm

class musicAnalzyer:
    
    def __init__(self, input_dir = r".\Training Data\train", onsetParams = {"batch_size":6,
                            "pow": 1.08},  minibatch_size = None, HFC = False):
        '''
        minibatch_size: [pos 1st file, pos last file - 1] in the input_dir\n
        useful when one does not wish to iterate over entire input_dir
        '''
        self.input_dir = Path(os.path.abspath(input_dir))
        # batch_size, pow
        self.onsetParams = onsetParams
        self.HFC = HFC
        self.evalValues = []
        self.input_dirLen = len(files_in_dir(self.input_dir))
        self.batchMult = 1
        if minibatch_size is None:
            minibatch_size = [0, self.input_dirLen]
        self.mb = minibatch_size
    
    def detectOnsets(self, plot = False, power = False):
        HFC = self.HFC
        inputted_files = files_in_dir(self.input_dir)[self.mb[0]:self.mb[1]]
        frame_length = 0
        
        for i, file in tqdm(enumerate(inputted_files), desc="Detecting Onsets",
                        total=len(inputted_files)):
            
            frame_energies, frame_length = calcFrameEnergies(file, HFC)
            
            if plot:
                plotSTFT(frame_energies, file)
                
            filePeaks = []
            batch_size = self.onsetParams["batch_size"]
            
            for value in range(batch_size*self.batchMult, frame_energies.size, batch_size*self.batchMult):
                file_pp_min =  ((frame_energies[value-batch_size*self.batchMult:value + batch_size*self.batchMult].mean() * self.onsetParams["pow"]))
                for subBatch in reversed(range(1, self.batchMult+1)):
                    for subVal in range(0, batch_size):
                        if (frame_energies[(subVal*subBatch) + (value- (batch_size* subBatch))] > file_pp_min):  
                            filePeaks.append((subVal) + (value- (batch_size* subBatch)))
                        
            self.logToFile(file, filePeaks, frame_length)

    def logToFile(self, file, filePeaks, frame_length):
        logfile = Path.joinpath(Path(self.input_dir),file.stem + ".onsets.pr")
        with logfile.open("w+") as f:
            for peak in filePeaks:
                f.write(f'{(peak * frame_length):0.9f}\n')
    
    def detectBeats(self):
        '''
        To be implimented
        '''
        pass
    
    def extractTempo(self):
        '''
        To be implimented
        '''
        pass
                        
    def copyFiles(self, newFolderName = None):
        '''
        Copies files from input_dir to new directory.\n
        newFolderName: if one wishes to seperate the files from each test set while updating set \n
        return copy_dir: pathlib Path to copied directory
        '''
        filesToCopy = files_in_dir(self.input_dir, "*.pr")
        if newFolderName is not None:  
            copy_dir = Path.joinpath(self.input_dir.parent,"predictions", str(newFolderName))
        else:
            copy_dir = Path.joinpath(self.input_dir.parent,"predictions")
        if not os.path.exists(copy_dir):
            os.makedirs(copy_dir)
        for file in filesToCopy:
            shutil.copy(str(file), str(Path.joinpath(copy_dir, file.name)))
            os.remove(str(file))
        return copy_dir

    def printEvalValues(self):
        '''
        prints formatted versions of all data stored in self.evalValues
        '''
        print(f" F-Measure            precision           recall       batch_size  pow     EvalType")
        for i in range(0, len(self.evalValues)):
            print(','.join(map(str,self.evalValues[i])))

    def evaluate(self, evalType = "onsets"):
        allEvalType = '*.' + evalType
        storeParams = [self.onsetParams['batch_size'], self.onsetParams['pow'], evalType.capitalize()]
        copied_dir = self.copyFiles(','.join(map(str,storeParams)))
        self.evalValues.append([evalFunc(files_in_dir(copied_dir, (allEvalType + ".pr"))[self.mb[0]:self.mb[1]],
                                        files_in_dir(self.input_dir, (allEvalType + ".gt"))[self.mb[0]:self.mb[1]])[:2], storeParams]) 
        logfile_name = str(copied_dir.parents._parts[-1] + ".log")
        logfile_dir = Path.joinpath(copied_dir,logfile_name)
        with logfile_dir.open("w+") as f:
            f.write(f" F-Measure            precision           recall       batch_size  pow \n")
            f.write(','.join(map(str,self.evalValues[0])))
        self.printEvalValues()

mA = musicAnalzyer(input_dir= r'.\Training Data\extras\onsets',HFC = True)
mA.detectOnsets()
mA.evaluate()

mA2 = musicAnalzyer(input_dir= r'.\Training Data\extras\onsets',HFC = False)
mA2.detectOnsets()
mA2.evaluate()