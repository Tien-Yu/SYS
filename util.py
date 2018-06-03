import datetime
import ftplib
import sys

def makeDestinationFullPath(ftp, sim, cuNum, patternType, serialID):
    rootPath = "/nobackup/d_10778_t1/tingchu10778" if sim == "d_sim" else "/nobackup/d_02168_t2/tingchu02168"
    dateString = datetime.datetime.today().strftime("%Y%m%d")
    cuPostfix = "single" if cuNum == "1" else "multi"
    dirname = dateString + "_" + patternType + "_" + cuPostfix + "_" + str(serialID)
    subID = 0
    flag = False
    if remoteDirExists(ftp, rootPath, dirname):
        dirname += "_"
        flag = True
    while remoteDirExists(ftp, rootPath, dirname + str(subID)):
        subID += 1
    if flag is True:
        dirname += str(subID)
    fullPath = rootPath + "/" + dirname
    return fullPath

def remoteDirExists(ftp, rootPath, dirname):
    filelist = []
    currentDir = ftp.pwd()
    ftp.cwd(rootPath)
    ftp.retrlines("LIST", filelist.append)
    for theFile in filelist:
        if theFile.split()[-1] == dirname and theFile.upper().startswith('D'):
            ftp.cwd(currentDir)
            return True
    ftp.cwd(currentDir)
    return False

def printStderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class ColorUtil:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLO = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    INFO = GREEN + "[Info]" + ENDC
    WARNING = YELLO + "[Warning]" + ENDC
    ERROR = RED + "[Error]" + ENDC
