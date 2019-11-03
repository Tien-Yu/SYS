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
from configparser import ConfigParser

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

            if self.path == "/test":
                self.path = "index.html"
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                file = open(os.curdir + os.sep + self.path)
                self.wfile.write(file.read().encode("utf-8"))
                file.close()
            elif self.path == "index.html":
                try:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    file = open(os.curdir + os.sep + self.path)
                    self.wfile.write(file.read().encode("utf-8"))
                    # self.wfile.write("<strong> MVPU Pattern Vending Machine 維護中，預計2018/8/6 17:00恢復，任何問題請聯絡 Tingchu</strong>".encode("Big5"))
                    file.close()
                except IOError as ioe:
                    self.send_error(404, "Incorrect path: {}".format(self.path))
            elif self.path == "/js/message":
                self.send_response(200)
                self.send_header('Content-type','text/plain')
                self.end_headers()
                self.wfile.write(self.sysServer.makeWelcomeMessage(clientIP).encode("utf-8"))
            elif self.path.startswith("/img/"):
                self.send_response(200)
                self.send_header('Content-type','')
                self.end_headers()
                with open(self.path.replace("/", "", 1), "rb") as itemfile:
                    self.wfile.write(itemfile.read())
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
                self.send_header('Content-type', '')
                self.end_headers()
                with open(self.path.replace("/", "", 1), "r") as itemfile:
                    self.wfile.write(itemfile.read().encode("utf-8"))
            elif self.path == "/favicon.ico":
                self.send_response(200)
                self.send_header('Content-type', 'image/x-icon')
                self.end_headers()
                with open("favicon.ico", "rb") as ico:
                    self.wfile.write(ico.read())
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
            ####### Arguments from web browser #######
            value_sim = form.getvalue("sim")
            value_cu_num = form.getvalue("cu_num")
            value_mem = form.getvalue("mem")
            value_parallel = form.getvalue("parallel")
            value_probe = form.getvalue("probe")
            value_non_conformance = form.getvalue("showSelectedNon")
            value_conformance = form.getvalue("showSelected")
            ##########################################

            # value_pattern_list = value_non_conformance.split(", ")
            value_pattern_list = []
            value_pattern_type = ""
            if value_non_conformance is not None and value_conformance is not None:
                value_pattern_list = value_non_conformance.split("\r\n") + value_conformance.split("\r\n")
                value_pattern_type = "mixed"
            elif value_non_conformance is not None and value_conformance is None:
                value_pattern_list = value_non_conformance.split("\r\n")
                value_pattern_type = "non_conformance"
            elif value_non_conformance is None and value_conformance is not None:
                value_pattern_list = value_conformance.split("\r\n")
                value_pattern_type = "conformance"
            else:
                value_pattern_type = "error"
            value_pattern_list = [x.strip() for x in value_pattern_list]
            value_pattern_list = list(filter(None, value_pattern_list))
            probeCfg = True if value_probe == "On" else False

            print(util.ColorUtil.INFO + "clientIP       : {}".format(self.client_address))
            print(util.ColorUtil.INFO + "sim            : {}".format(value_sim))
            print(util.ColorUtil.INFO + "cu_num         : {}".format(value_cu_num))
            print(util.ColorUtil.INFO + "mem            : {}".format(value_mem))
            print(util.ColorUtil.INFO + "parallel       : {}".format(value_parallel))
            print(util.ColorUtil.INFO + "probe          : {}".format(value_probe))
            print(util.ColorUtil.INFO + "non            : {}".format(value_pattern_list))
            # print(util.ColorUtil.INFO + "Non-Conformance: {}".format(value_non_conformance))
            # print(util.ColorUtil.INFO + "Conformance    : {}".format(value_conformance))
            # print(util.ColorUtil.INFO + "pattern list   : {}".format(value_pattern_list))

            if self.path == "index.html":
                clientIP = self.client_address[0]
                result = {} # result below should be a 2D json, for javascript
                code = 404
                if value_pattern_type == "error":
                    result = self.sysServer.makeWelcomeMessage(clientIP, noPatternError=True)
                    code = 404
                else:
                    value_cu_num = "1" if value_cu_num == "single" else "2"
                    result = self.sysServer.createChild(value_sim, value_cu_num, value_mem, value_parallel, probeCfg, value_pattern_type, value_pattern_list, clientIP)
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

    def createChild(self, simType, cuNum, mem, parallel, probe, patternType, patternList, clientIP):
        if util.isDevMode():
            return True
        regressPath = self.dispatchRegressionWorkspace()
        if regressPath == -1:
            dictMsg = {0: {0: "All three workspaces are busy."}}
            return json.dumps(dictMsg)

        if self.checkIP(clientIP, regressPath) is False:
            dictMsg = {0: {0: "You already have a job (ID: {}) running".format(self.clientInfo[clientIP].serialID)}}
            return json.dumps(dictMsg)

        cmd = self.makeCommand(simType, cuNum, mem, probe, parallel, patternType, patternList, regressPath)
        self.syslog("[Job {}][{}] Command: {}".format(self.serialNumber, clientIP, cmd))
        child = Popen(cmd.split(), stdout=PIPE)
        mosesqMessage = child.stdout.readline().decode("utf-8")
        match = re.match(r"Job <(.*)> (.*)", mosesqMessage)
        mosesqID = match.group(1)

        projectID = "10778" if simType == "d_sim" else "02168"
        ftp = None
        if simType != "fpga" and simType != "dbg_info":
            ftp = ftplib.FTP("Mtkftp1")
            ftp.login("tingchu" + projectID, util.ftpPassword())
        self.clientInfo[clientIP].destDir = util.makeDestinationFullPath(ftp, simType, cuNum, patternType, self.serialNumber)
        self.clientInfo[clientIP].process = child
        self.clientInfo[clientIP].mosesqJobID = mosesqID
        self.clientInfo[clientIP].patternCount = len(patternList)
        self.serialNumber += 1
        if simType != "fpga" and simType != "dbg_info":
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
                        print(util.ColorUtil.WARNING + " The job of client {} is being force stopped".format(ip).strip())
                        self.syslog("bkill " + info.mosesqJobID)
                        os.system("bkill " + info.mosesqJobID)
                        info.process.kill()
                        info.cleanUp()
                        print("Done")
                    else:
                        maxline = 10
                        linecount = 0
                        line = info.process.stdout.readline()
                        while line:
                            print(line.decode("utf-8"), end="")
                            line = info.process.stdout.readline()
                            linecount += 1
                            if linecount >= maxline:
                                break

                else:
                    info.cleanUp()
                    self.syslog("Done the job of client {}".format(ip))
            else:
                print(" --- process is None!")

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
        dictMsg = {}
        dictMsg[0] = {}
        dictMsg[1] = {}
        dictMsg[2] = {}
        dictMsg[3] = {}
        dictMsg[4] = {}
        dictMsg[5] = {}
        dictMsg[6] = {}
        currentHAVEcommitMsg = self.getLatestHAVEcommitMsg()
        msg0 = currentHAVEcommitMsg.split("|")[0]
        msg1 = currentHAVEcommitMsg.split("|")[1]
        msg2 = currentHAVEcommitMsg.split("|")[2]
        if noPatternError is True:
            dictMsg[0][0] = "No pattern selected"
        elif ip in self.clientInfo:
            info = self.clientInfo[ip]
            if info.jobCount <= 0:
                dictMsg[0][0] = "Welcome back! You have no jobs in progress. Previous pattern locations: "
                dictMsg[1][0] = "<strong>" + info.destDir + "</strong>"
                dictMsg[2][0] = msg0
                dictMsg[3][0] = msg1
                dictMsg[4][0] = msg2
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
                    dictMsg[0][0] = "MVPU PVM received your job, ID: "
                    dictMsg[0][1] = "<strong>" + "{}".format(info.serialID) + "</strong>"
                    dictMsg[0][2] = "."
                    dictMsg[1][0] = "Patterns processed/total : <strong>{} / {}</strong>".format(processedPatternCount, info.patternCount)
                    dictMsg[2][0] = "You'll get your patterns in "
                    dictMsg[2][1] = "<strong>" + info.destDir + "</strong>"
                    dictMsg[3][0] = msg0
                    dictMsg[4][0] = msg1
                    dictMsg[5][0] = msg2
                else:
                    dictMsg[0][0] = "Currently you have {} job (ID: ".format(info.jobCount)
                    dictMsg[0][1] = "<strong>" + "{}".format(info.serialID) + "</strong>"
                    dictMsg[0][2] = ") still running."
                    dictMsg[1][0] = "Patterns processed/total : <strong>{} / {}</strong>".format(processedPatternCount, info.patternCount)
                    dictMsg[2][0] = "You'll get your patterns in "
                    dictMsg[3][0] = "<strong>" + info.destDir + "</strong>"
                    dictMsg[4][0] = msg0
                    dictMsg[5][0] = msg1
                    dictMsg[6][0] = msg2
        else:
            dictMsg[0][0] = "Welcome! You have no jobs currently running."
            dictMsg[1][0] = msg0
            dictMsg[2][0] = msg1
            dictMsg[3][0] = msg2
        jsonMsg = json.dumps(dictMsg)
        print(jsonMsg)
        print(type(dictMsg))
        return jsonMsg

    def getLatestHAVEcommitMsg(self):
        if util.isDevMode():
            return "AA|BB|CC"
        curdir = os.getcwd()
        prefix = "Latest HAVE commit: "
        os.chdir("/proj/mtk10109/mtk_git/have3/HAVE")

        process = Popen("git rev-parse HEAD".split(), stdout=PIPE)
        out, err = process.communicate()
        commit = out.decode("utf-8").strip()

        process2 = Popen("git log HEAD~1..HEAD --format=%cd".split(), stdout=PIPE)
        out2, err2 = process2.communicate()
        dateStr = out2.decode("utf-8").strip()

        process3 = Popen("git log HEAD~1..HEAD --pretty=format:%s".split(), stdout=PIPE)
        out3, err3 = process3.communicate()
        title = out3.decode("utf-8").strip()
        if commit == "7d2132ccf93a160feeca1686eb44add8b5da6e00":    # jenjung's force inorder patch
            process = Popen("git rev-parse HEAD~1".split(), stdout=PIPE)
            out, err = process.communicate()
            commit = out.decode("utf-8").strip()
            process2 = Popen("git log HEAD~2..HEAD~1 --format=%cd".split(), stdout=PIPE)
            out2, err2 = process2.communicate()
            dateStr = out2.decode("utf-8").strip()
        os.chdir(curdir)
        return "{}|{}|{}".format(prefix + commit, dateStr, title)

    def makeCommand(self, simType, cuNum, mem, probe, parallel, patternType, patternList, regressPath):
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

        havePath = 2
        # if simType == "cu_sim":
        #     havePath = 3
        probeCfg = "-probe" if probe is True else ""
        parallelCfg = "-parallel" if parallel == "1" else ""
        cmd = "mosesq time python3 genPatternFromfile.py -file {} -sim {} -cu {} -mem {} {} -pattern_type {} {} -delete -upload -have_path {} -regression_path {} -serialID {}".format(inputFilename, simType, cuNum, mem, parallelCfg, patternType, probeCfg, havePath, regressPath, self.serialNumber)

        return cmd

    def cdToRegressionPath(self, regressPath):
        if regressPath == 0:
            os.chdir("../HAVE-Regression/")
        elif regressPath == 1:
            os.chdir("../regression2/HAVE-Regression")
        elif regressPath == 2:
            os.chdir("../regression3/HAVE-Regression")
        else:
            assert False

    def syslog(self, message, printToScreen=True):
        self.logfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " ")
        self.logfile.write(message + "\n")
        self.logfile.flush()
        if printToScreen is True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print(message)

    def dispatchRegressionWorkspace(self):
        if not os.listdir("../HAVE-Regression/out/"):    # workspace 0 is empty, available
            return 0
        elif not os.listdir("../regression2/HAVE-Regression/out"): # workspace 1 is empty, available
            return 1
        elif not os.listdir("../regression3/HAVE-Regression/out"): # workspace 2 is empty, available
            config = ConfigParser()
            config.read('sys.cfg')
            # config.add_section('main')
            # config.set('main', 'quick_job_slot', "1")
            if config.getint("main", "quick_job_slot") >= 1:    # Allow the 3rd workspace for quick jobs
                return 2
            else:
                return -1
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
