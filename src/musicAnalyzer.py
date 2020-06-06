from framework import *
import shutil
from tqdm import tqdm

class musicAnalzyer:
    
    def __init__(self, input_dir = r".\Training Data\train", subsetPositions = None, HFC = False, plot = False):
        '''
        input_dir = str path to directory containing .wav files and .gt files\n
        subsetPositions: indexes of subset of files in input_dir over which to iterate\n
        HFC: if true -> calcFrameOnsets weights bins for High Frequency Content\n
        plot: if true will plot calc amplitude vs frame graph for each .wav file
        
        '''
        self.input_dir = Path(os.path.abspath(input_dir))
        self.onsetParams = {"batch_size":6,
                            "pow": 1.08}
        self.HFC = HFC
        self.plot = plot
        self.evalValues = []
        self.input_dirLen = len(files_in_dir(self.input_dir))
        self.batchMult = 1
        if subsetPositions is None:
            subsetPositions = [0, self.input_dirLen]
        self.mb = subsetPositions
    
    def detectOnsets(self):
        print("Detecting Onsets..")
        HFC = self.HFC
        inputted_files = files_in_dir(self.input_dir)[self.mb[0]:self.mb[1]]
        frame_length = 0
        
        for i, file in tqdm(enumerate(inputted_files), desc="Detecting Onsets",
                        total=len(inputted_files)):
            
            frame_energies, frame_length = calcFrameEnergies(file, HFC)
            
            if self.plot:
                plotSTFT(frame_energies, file)
                
            filePeaks = []
            batch_size = self.onsetParams["batch_size"]
            for value in range(batch_size, frame_energies.size, batch_size):
                file_pp_min =  ((frame_energies[value-batch_size:value + batch_size].mean() * self.onsetParams["pow"]))
                for subVal in range(0, batch_size):
                    if (frame_energies[subVal + (value- batch_size)] > file_pp_min):  
                        filePeaks.append(subVal + (value- batch_size))
                            
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
    
    def analyze(self, output = False):
        '''
        Evaluates given input directory for onsets, beats, and tempo
        output: if true -> will evaluate all three for F-measures
        '''
        print("Analyzing Directory")
        self.detectOnsets()
        self.detectBeats()
        self.extractTempo()
        if output:
                print("Evaluating predictions")
                self.evaluate("onsets")
                self.evaluate("beats")
                self.evaluate("tempo")                       
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

    def evaluate(self, evalType = "onsets"):
        '''
        Run eval on evalType and create log file
        '''
        allEvalType = '*.' + evalType
        storeParams = [self.onsetParams['batch_size'], self.onsetParams['pow'], evalType.capitalize()]
        copied_dir = self.copyFiles(','.join(map(str,storeParams)))
        self.evalValues.append([evalFunc(files_in_dir(copied_dir, (allEvalType + ".pr"))[self.mb[0]:self.mb[1]],
                                        files_in_dir(self.input_dir, (allEvalType + ".gt"), evalType)[self.mb[0]:self.mb[1]])[:2],
                                         storeParams]) 
        logfile_name = str(copied_dir.parents._parts[-1] + ".log")
        logfile_dir = Path.joinpath(copied_dir,logfile_name)
        with logfile_dir.open("w+") as f:
            f.write(f" F-Measure            precision           recall       batch_size  pow \n")
            f.write(','.join(map(str,self.evalValues[0])))
        self.printEvalValues()

    def printEvalValues(self):
        '''
        prints formatted versions of all data stored in self.evalValues
        '''
        print(f" F-Measure            precision           recall       batch_size  pow     EvalType")
        for i in range(0, len(self.evalValues)):
            print(','.join(map(str,self.evalValues[i])))
            
