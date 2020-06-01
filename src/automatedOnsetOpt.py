from detectOnsets import *
import shutil

class onsetOptimizer:
    def __init__(self, input_dir, minibatch_size = None):
        self.input_dir = Path(os.path.abspath(input_dir))
        self.defaultHyperParams = [7,0.99, 150]
        self.hyperParams = [0,0,0]
        self.avgValues = []
        self.iteration = 0
        self.input_dirLen = len(files_in_dir(input_dir))
        if minibatch_size is None:
            minibatch_size = [0, self.input_dirLen]
        self.mb = minibatch_size
        
    def update(self, updateVals, updateStep = [1, 0.05, 25]):
        for j in range(0, len(updateVals)):
            self.hyperParams[j] = self.defaultHyperParams[j] + (updateVals[j] * updateStep[j])
    
    def doOnsetDetection(self):
        detectOnsets(self.input_dir, self.hyperParams[0], 
                     self.hyperParams[1], self.hyperParams[2], [self.mb[0],self.mb[1]])
    
    def copyFiles(self, newFolderName):
        
        filesToCopy = files_in_dir(self.input_dir, "*.pr")
        copy_dir = Path.joinpath(self.input_dir.parent,"eval", str(newFolderName))
        if not os.path.exists(copy_dir):
            os.makedirs(copy_dir)
        for file in filesToCopy:
            shutil.copy(str(file), str(Path.joinpath(copy_dir, file.name)))
        return copy_dir
    
    def evaluate(self):
        storeParams = [self.hyperParams[0], self.hyperParams[1], self.hyperParams[2]]
        storeIter = np.append([int(self.iteration)], np.array(storeParams))
        copied_dir = self.copyFiles(','.join(map(str,storeIter)))
        self.avgValues.append([evalFunc(files_in_dir(copied_dir, "*.pr")[self.mb[0]:self.mb[1]],
                                        files_in_dir(self.input_dir, "*.onsets.gt")[self.mb[0]:self.mb[1]])[:2], storeParams]) 
        logfile_name = str(copied_dir.parents._parts[-1] + ".log")
        logfile_dir = Path.joinpath(copied_dir,logfile_name)
        with logfile_dir.open("w+") as f:
            f.write(f"% True Positives      CumulatError [s]  AvgTp AvgFp AvgFn  batch pow sampLen \n")
            f.write(','.join(map(str,self.avgValues[self.iteration]))) 
        self.iteration += 1   
        
        
onset = onsetOptimizer(r"C:\Users\brenn\iCloudDrive\College\Y2S2\Classes\0 Audio Processing\REPO\Reptile-Tornadoes\Training Data\train")
initialSetupParams = [[0,0,0],[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
for i in range(0,len(initialSetupParams)):
    onset.update(initialSetupParams[i])
    onset.doOnsetDetection()
    onset.evaluate()
final_log = Path.joinpath(onset.input_dir,"final.log")
with final_log.open("w+") as f:
    f.write(f"% True Positives      CumulatError [s]  AvgTp AvgFp AvgFn  batch pow sampLen \n")
    for i in range(0, len(onset.avgValues)):
        f.write(','.join(map(str,onset.avgValues[i])))