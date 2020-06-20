from framework import *
import shutil
from tqdm import tqdm


class musicAnalzyer:
    def __init__(self, input_dir=r".\test", subsetPositions=None, HFC=True, plot=False):
        '''
        input_dir = str path to directory containing .wav files and .gt files\n
        subsetPositions: indexes of subset of files in input_dir over which to iterate\n
        HFC: if true -> calcFrameOnsets weights bins for High Frequency Content\n
        plot: if true will plot calc amplitude vs frame graph for each .wav file

        '''
        self.input_dir = Path(os.path.abspath(input_dir))
        self.onsetParams = {"batch_size": 6,
                            "pow": 1.08}
        self.HFC = HFC
        self.plot = plot
        self.evalValues = []
        self.input_dirLen = len(files_in_dir(self.input_dir))
        if subsetPositions is None:
            subsetPositions = [0, self.input_dirLen]
        self.mb = subsetPositions
        self.inputted_files = files_in_dir(self.input_dir)[self.mb[0]:self.mb[1]]

    def detectOnsets(self):
        print("Detecting Onsets..")
        HFC = self.HFC
        frame_length = 0

        for i, file in tqdm(enumerate(self.inputted_files), total=len(self.inputted_files)):

            frame_energies, frame_length = calcFrameEnergies(file, HFC)

            if self.plot:
                plotSTFT(frame_energies, file)

            filePeaks = []
            batch_size = self.onsetParams["batch_size"]
            for value in range(batch_size, frame_energies.size, batch_size):
                file_pp_min = (
                    (frame_energies[value-batch_size:value + batch_size].mean() * self.onsetParams["pow"]))
                for subVal in range(0, batch_size):
                    if (frame_energies[subVal + (value - batch_size)] > file_pp_min):
                        filePeaks.append(subVal + (value - batch_size))

            filePeaks = clearExcess(filePeaks)
            logfile = Path.joinpath(
                Path(self.input_dir), file.stem + ".onsets.pr")
            with logfile.open("w+") as f:
                for peak in filePeaks:
                    f.write(f'{(peak * frame_length):0.9f}\n')

    def extractTempo(self):
        '''
        calculates all IOI's for a given piece. if theyre larger than .2seconds (300bpm) add them to the list of IOI's
        calc tempo for piece, if tempo is over 200BPM then divide by 2 as it is an octave error.
        '''
        onsets = files_in_dir(self.input_dir, '*.onsets.pr')
        for i, file in tqdm(enumerate(onsets), total=len(onsets)):
            onsetList = importListFromFile(file)
            interOnsetList = [];
            for i in range(1, len(onsetList)):
                interOnset = onsetList[i] - onsetList[i-1]
                if interOnset >= 0.2 and interOnset <= 1:
                    interOnsetList.append(interOnset)     
            interOnsetList =np.asarray(interOnsetList)
            tempo = 60/interOnsetList.mean()
            if tempo > 200:
                tempo /= 2
            logfile = Path.joinpath(Path(self.input_dir), file.stem[:-7] + ".tempo.pr")
            with logfile.open("w+") as f:
                f.write(f'{(tempo):0.9f}\n')

    def detectBeats(self):
        '''
        To be implimented

        I DONT RLY GET THIS

        soooo logically, when i figure out the bpm, i can back track on the onset where 
        those beets are by looking at what position the in the IOI's were the ones who are = to the decided lag
                        ^
                       /I\
                        I
                        I
                    I dont think this works i was looking at the beats.gt and none of the numbers match any number within the onset.gt also after each beat there is some
                    number idk why or what it is.



        ummm.... soo what im thinking is i get the Tempo value ( lag ) from the bpm, and have it like
        ( guessing that the code is run to find everything at once ( saying this cause of the song duration) )
        to have 
        duration = librosa.get_duration( filename= "input_dir")         #returns it in seconds ( like a float )
        then have a array save beats like

        x = []
        lag = 60/Tempo
        i = 0
        j = 1
        while x[i] < duration:
            x[i] = lag * j
            if x[i] < duration:
                break
            i++
            j++

        then just print it the same way as u did in the OnSet function
        
        '''
        # Tempo = clearExcess(importListFromFile(self.input_dir)) # or is just self.input_dir enough


        pass

    def analyze(self, output=False):
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

    def copyFiles(self, newFolderName=None):
        '''
        Copies files from input_dir to new directory.\n
        newFolderName: if one wishes to seperate the files from each test set while updating set \n
        return copy_dir: pathlib Path to copied directory
        '''
        filesToCopy = files_in_dir(self.input_dir, "*.pr")
        if newFolderName is not None:
            copy_dir = Path.joinpath(
                self.input_dir.parent, "predictions", str(newFolderName))
        else:
            copy_dir = Path.joinpath(self.input_dir.parent, "predictions")
        if not os.path.exists(copy_dir):
            os.makedirs(copy_dir)
        for file in filesToCopy:
            shutil.copy(str(file), str(Path.joinpath(copy_dir, file.name)))
            os.remove(str(file))
        return copy_dir

    def evaluate(self, evalType="onsets"):
        '''
        Run eval on evalType and create log file
        '''
        allEvalType = '*.' + evalType
        storeParams = [self.onsetParams['batch_size'],
                       self.onsetParams['pow'], evalType.capitalize()]
        copied_dir = self.copyFiles(','.join(map(str, storeParams)))
        self.evalValues.append([evalFunc(files_in_dir(copied_dir, (allEvalType + ".pr"))[self.mb[0]:self.mb[1]],
                                         files_in_dir(self.input_dir, (allEvalType + ".gt"))[self.mb[0]:self.mb[1]], evalType)[:2],
                                storeParams])
        logfile_name = str(copied_dir.parents._parts[-1] + ".log")
        logfile_dir = Path.joinpath(copied_dir, logfile_name)
        with logfile_dir.open("w+") as f:
            f.write(
                f" F-Measure            precision           recall       batch_size  pow \n")
            f.write(','.join(map(str, self.evalValues[0])))
        self.printEvalValues()

    def printEvalValues(self):
        '''
        prints formatted versions of all data stored in self.evalValues
        '''
        print(f" F-Measure            precision           recall       batch_size  pow     EvalType")
        for i in range(0, len(self.evalValues)):
            print(','.join(map(str, self.evalValues[i])))


mA = musicAnalzyer()
mA.extractTempo()
