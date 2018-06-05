from __future__ import print_function
import sys
import os
import cgi
import time
import util
import ftplib
import re
import json
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from subprocess import Popen, PIPE
from threading import Thread

def makeHandlerFromArguments(myServer):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.sysServer = myServer
            super(RequestHandler, self).__init__(*args, **kwargs)

        def do_GET(self):
            if self.path == "/":
                self.path = "index.html"
            print("GET path {}".format(self.path))
            print("clientIP : {}".format(self.client_address))
            clientIP = self.client_address[0]

            if self.path == "index.html":
                try:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    file = open(os.curdir + os.sep + self.path)
                    self.wfile.write(file.read().encode("utf-8"))
                    file.close()
                except IOError as ioe:
                    self.send_error(404, "Incorrect path: {}".format(self.path))
            elif self.path == "/js/message":
                self.send_response(200)
                self.send_header('Content-type','text/plain')
                self.end_headers()
                self.wfile.write(self.sysServer.makeWelcomeMessage(clientIP).encode("utf-8"))
            elif self.path == "/img/bg2.jpg":
                self.send_response(200)
                self.send_header('Content-type','image/jpg')
                self.end_headers()
                with open("img/bg2.jpg", "rb") as bg:
                    self.wfile.write(bg.read())
            elif self.path == "/css/sys.css":
                self.send_response(200)
                self.send_header('Content-type','text/css')
                self.end_headers()
                with open("css/sys.css", "r") as css:
                    self.wfile.write(css.read().encode("utf-8"))
            elif self.path.startswith("/js/"):
                self.send_response(200)
                self.send_header('Content-type','')
                self.end_headers()
                opentype = ""
                if self.path.endswith("png"):
                    opentype = "rb"
                else:
                    opentype = "r"
                with open(self.path.replace("/", "", 1), opentype) as itemfile:
                    if opentype == "rb":
                        self.wfile.write(itemfile.read())
                    else:
                        self.wfile.write(itemfile.read().encode("utf-8"))
                # for rootpath, dirnames, filenames in os.walk("js/jquery-ui-1.12.1"):
                    # for item in filenames:
                    #     itemfile = open(os.path.join(rootpath, item), "r")
                    #     self.wfile.write(itemfile.read())
            elif self.path.startswith("/data/"):
                self.send_response(200)
                self.send_header('Content-type','')
                self.end_headers()
                with open(self.path.replace("/", "", 1), "r") as itemfile:
                    self.wfile.write(itemfile.read().encode("utf-8"))
            else:
                self.send_error(404, "Incorrect path: {}".format(self.path))

        def do_POST(self):
            if self.path == "/":
                self.path = "index.html"
            print("POST path {}".format(self.path))
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            value_sim = form.getvalue("sim")
            value_cu_num = form.getvalue("cu_num")
            value_mem = form.getvalue("mem")
            value_probe = form.getvalue("probe")
            value_non_conformance = form.getvalue("showSelectedNon")
            value_conformance = form.getvalue("showSelected")
            # value_pattern_list = value_non_conformance.split(", ")
            value_pattern_list = []
            value_pattern_type = ""
            if value_non_conformance is not None and value_conformance is not None:
                value_pattern_list = value_non_conformance.split(", ") + value_conformance.split(", ")
                value_pattern_type = "mixed"
            elif value_non_conformance is not None and value_conformance is None:
                value_pattern_list = value_non_conformance.split(", ")
                value_pattern_type = "non_conformance"
            elif value_non_conformance is None and value_conformance is not None:
                value_pattern_list = value_conformance.split(", ")
                value_pattern_type = "conformance"
            else:
                value_pattern_type = "error"
            probeCfg = True if value_probe == "On" else False

            print(util.ColorUtil.INFO + "clientIP       : {}".format(self.client_address))
            print(util.ColorUtil.INFO + "sim            : {}".format(value_sim))
            print(util.ColorUtil.INFO + "cu_num         : {}".format(value_cu_num))
            print(util.ColorUtil.INFO + "mem            : {}".format(value_mem))
            print(util.ColorUtil.INFO + "probe          : {}".format(value_probe))
            #print(util.ColorUtil.INFO + "Non-Conformance: {}".format(value_non_conformance))
            #print(util.ColorUtil.INFO + "Conformance    : {}".format(value_conformance))
            # print(util.ColorUtil.INFO + "pattern list   : {}".format(value_pattern_list))

            if self.path == "index.html":
                clientIP = self.client_address[0]
                result = "Default error"
                code = 404
                if value_pattern_type == "error":
                    result = self.sysServer.makeWelcomeMessage(clientIP, noPatternError=True)
                    code = 404
                else:
                    value_cu_num = "1" if value_cu_num == "single" else "2"
                    result = self.sysServer.createChild(value_sim, value_cu_num, value_mem, probeCfg, value_pattern_type, value_pattern_list, clientIP)
                    code = 200 if result == True else 507

                if result == True:
                    try:
                        self.send_response(code)
                        self.send_header('Content-type','text/html')
                        self.end_headers()
                        self.wfile.write(self.sysServer.makeWelcomeMessage(clientIP, isPost=True).encode("utf-8"))
                    except IOError as ioe:
                        self.send_error(404, "Incorrect path: {}".format(self.path))
                else:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(result.encode("utf-8"))
            else:
                self.send_error(404, "Incorrect path: {}".format(self.path))

    return RequestHandler

class SYSServer():
    def __init__(self, port):
        self.port = port
        self.handlerClass = makeHandlerFromArguments(self)
        self.clientInfo = dict()
        self.logfile = open("sys.log", "a")
        self.stop = False
        self.serialNumber = 0

    def start(self):
        try:
            serverThread = Thread(target=self.startServer, args=[])
            serverThread.start()
            while self.stop is False:
                time.sleep(2)
                self.pollChildren()

        except KeyboardInterrupt:
            print("\n" + util.ColorUtil.INFO + "Close server")
            self.logfile.close()

    def startServer(self):
        serverAddress = ("", self.port)
        server = HTTPServer(serverAddress, self.handlerClass)

        print(util.ColorUtil.INFO + " Started httpserver on port {}".format(self.port))
        # Wait forever for incoming http requests
        server.serve_forever()

    def createChild(self, simType, cuNum, mem, probe, patternType, patternList, clientIP):
        return True
        regressPath = self.dispatchRegressionWorkspace()
        if regressPath == -1:
            return "All three workspaces are busy."

        if self.checkIP(clientIP, regressPath) is False:
            return "You already have a job (ID: {}) running".format(self.clientInfo[clientIP].serialID)

        cmd = self.makeCommand(simType, cuNum, mem, probe, patternType, patternList, regressPath)
        self.syslog("[Job {}][{}] Command: {}".format(self.serialNumber, clientIP, cmd))
        child = Popen(cmd.split(), stdout=PIPE)
        # child = Popen("qq ls".split(), stdout=PIPE)
        mosesqMessage = child.stdout.readline().decode("utf-8")
        match = re.match(r"Job <(.*)> (.*)", mosesqMessage)
        mosesqID = match.group(1)

        projectID = "10778" if simType == "d_sim" else "02168"
        ftp = ftplib.FTP("Mtkftp1")
        ftp.login("tingchu" + projectID, "mediatek")
        self.clientInfo[clientIP].destDir = util.makeDestinationFullPath(ftp, simType, cuNum, patternType, self.serialNumber)
        self.clientInfo[clientIP].process = child
        self.clientInfo[clientIP].mosesqJobID = mosesqID
        self.clientInfo[clientIP].patternCount = len(patternList)
        self.serialNumber += 1
        ftp.quit()
        self.syslog("Destination path: {}".format(self.clientInfo[clientIP].destDir))
        return True

    def pollChildren(self):
        for ip in list(self.clientInfo):
            info = self.clientInfo[ip]
            if info.jobCount == 0:
                continue

            if info.process is not None:
                code = info.process.poll()
                if code is None: # still running
                    if self.checkForceStop(info):
                        print(util.ColorUtil.WARNING + " The job of client {} is being force stopped".format(ip))
                        self.syslog("bkill " + info.mosesqJobID)
                        os.system("bkill " + info.mosesqJobID)
                        info.process.kill()
                        info.cleanUp()
                        print("Done")
                    else:
                        line = info.process.stdout.readline()
                        while line:
                            print(line.decode("utf-8"), end="")
                            line = info.process.stdout.readline()
                else:
                    info.cleanUp()
                    self.syslog("Done the job of client {}".format(ip))
            else:
                print("--- process is None !!!")

    def checkForceStop(self, info):
        if os.path.exists("stop{}.cfg".format(info.regressPath)):
            return True
        return False

    def checkIP(self, ip, regressPath): # Check if 'ip' can fire a job
        if ip in self.clientInfo:
            if self.clientInfo[ip].jobCount <= 0:
                self.clientInfo[ip].jobCount = 1
                self.clientInfo[ip].serialID = self.serialNumber
                self.clientInfo[ip].regressPath = regressPath
                return True
            else:
                self.syslog("Client {} already has a job (ID: {}) running".format(ip, self.clientInfo[ip].serialID))
        else:
            info = ClientInfo(ip)
            self.clientInfo[ip] = info
            self.clientInfo[ip].jobCount = 1
            self.clientInfo[ip].serialID = self.serialNumber
            self.clientInfo[ip].regressPath = regressPath
            return True
        return False

    def makeWelcomeMessage(self, ip, noPatternError=False, isPost=False):
        jsonMsg = ""
        dictMsg = dict()
        if noPatternError is True:
            dictMsg["first"] = "No pattern selected"
        elif ip in self.clientInfo:
            info = self.clientInfo[ip]
            if info.jobCount <= 0:
                dictMsg["first"] = "Welcome back! You have no jobs in progress. Previous pattern locations: "
                dictMsg["path"] = info.destDir
            else:
                curdir = os.getcwd()
                self.cdToRegressionPath(info.regressPath)
                processedPatternCount = 0
                try:
                    with open("out/pattern_count.txt", "r") as countFile:
                        processedPatternCount = countFile.readline()
                except:
                    pass

                os.chdir(curdir)
                if isPost is True:
                    dictMsg["first"] = "SYS received your job, ID: "
                    dictMsg["idVal"] = "{}".format(info.serialID)
                    dictMsg["second"] = ". Patterns processed/total : {} / {}".format(processedPatternCount, info.patternCount)
                    dictMsg["third"] = "You'll get your patterns in "
                    dictMsg["path"] = info.destDir
                else:
                    dictMsg["first"] = "Currently you have {} job (ID: ".format(info.jobCount)
                    dictMsg["idVal"] = "{}".format(info.serialID)
                    dictMsg["second"] = ") still running. Patterns processed/total : {} / {}".format(processedPatternCount, info.patternCount)
                    dictMsg["third"] = "You'll get your patterns in "
                    dictMsg["path"] = info.destDir
        else:
            dictMsg["first"] = "Welcome! You have no jobs currently running."
        jsonMsg = json.dumps(dictMsg)
        print(jsonMsg)
        return jsonMsg

    def makeCommand(self, simType, cuNum, mem, probe, patternType, patternList, regressPath):
        inputFilename = "templist" + str(self.serialNumber) + ".txt"
        if not patternList:
            inputFilename = "group_non_conformance.txt"
        else:
            curdir = os.getcwd()
            self.cdToRegressionPath(regressPath)

            newlineList = [line + "\n" for line in patternList]
            with open(inputFilename, "w") as infile:
                infile.writelines(newlineList)

            os.chdir(curdir)

        probeCfg = "-probe" if probe is True else ""
        cmd = "mosesq time python3 genPatternFromfile.py -file {} -sim {} -cu {} -mem {} -pattern_type {} {} -delete -upload -have_path 2 -regression_path {} -serialID {}".format(inputFilename, simType, cuNum, mem, patternType, probeCfg, regressPath, self.serialNumber)

        return cmd

    def cdToRegressionPath(self, regressPath):
        if regressPath == 0:
            os.chdir("../HAVE-Regression/")
        elif regressPath == 1:
            os.chdir("../regression2/HAVE-Regression")
        else:
            os.chdir("../regression3/HAVE-Regression")

    def syslog(self, message, printToScreen=True):
        self.logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ")
        self.logfile.write(message + "\n")
        self.logfile.flush()
        if printToScreen is True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            print(message)

    def dispatchRegressionWorkspace(self):
        if not os.listdir("../HAVE-Regression/out/"):    # workspace 0 is empty, available
            return 0
        elif not os.listdir("../regression2/HAVE-Regression/out"): # workspace 1 is empty, available
            return 1
        # elif not os.listdir("../regression3/HAVE-Regression/out"): # workspace 1 is empty, available
        #     return 2
        else:
            return -1

    # def modifyHtmlMessage(self, newMsg):
    #     keyword = "<p id=\"message\" name=\"message\">"
    #     htmlfile = open("index.html", "r")
    #     lines = htmlfile.readlines()
    #     for idx, line in enumerate(lines):
    #         if keyword in line:
    #             lines[idx] = "        <p id=\"message\" name=\"message\">{}</p>\n".format(newMsg)
    #     htmlfile.close()

    #     htmlfile = open("index.html", "w")
    #     htmlfile.writelines(lines)
    #     htmlfile.close()


class ClientInfo:
    def __init__(self, ip):
        self.ip = ip
        self.destDir = ""
        self.serialID = -1
        self.cleanUp()

    def cleanUp(self):
        self.jobCount = 0
        # self.serialID = -1
        # self.destDir = ""
        self.regressPath = -1
        self.process = None
        self.mosesqJobID = ""
        self.patternCount = 0

def main():
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 2454
    
    server = SYSServer(port)
    server.start()

if __name__ == '__main__':
    main()
