from __future__ import print_function
import sys
import os
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import cgi


#Handler for the GET requests
class requestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "index.html"
        

        print("GET path {}".format(self.path))

        if self.path == "index.html":
            try:
                file = open(os.curdir + os.sep + self.path)
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(file.read())
                file.close()
            except IOError as ioe:
                self.send_error(404, "Incorrect path: {}".format(self.path))
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
                self.wfile.write(css.read())
        elif self.path.startswith("/js/"):
        # elif self.path == "/js/jquery-ui-1.12.1/jquery-ui.css":
            self.send_response(200)
            self.send_header('Content-type','')
            self.end_headers()
            opentype = ""
            if self.path.endswith("png"):
                opentype = "rb"
            else:
                opentype = "r"
            with open(self.path.replace("/", "", 1), opentype) as itemfile:
                self.wfile.write(itemfile.read())
            # for rootpath, dirnames, filenames in os.walk("js/jquery-ui-1.12.1"):
                # for item in filenames:
                #     itemfile = open(os.path.join(rootpath, item), "r")
                #     self.wfile.write(itemfile.read())
        elif self.path.startswith("/data/"):
            self.send_response(200)
            self.send_header('Content-type','')
            self.end_headers()
            with open(self.path.replace("/", "", 1), "r") as itemfile:
                self.wfile.write(itemfile.read())
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
        print("sim   : {}".format(form.getvalue("sim")))
        print("cu_num: {}".format(form.getvalue("cu_num")))
        print("mem   : {}".format(form.getvalue("mem")))
        print("Non-Conformance: {}".format(form.getvalue("showSelectedNon")))
        print("Conformance: {}".format(form.getvalue("showSelected")))

        # print("form:", form)

        if self.path == "index.html":
            try:
                file = open(os.curdir + os.sep + self.path)
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write("Success!")
                file.close()
            except IOError as ioe:
                self.send_error(404, "Incorrect path: {}".format(self.path))
        else:
            self.send_error(404, "Incorrect path: {}".format(self.path))

def main():
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 11605
    
    # serverAddress = ('127.0.0.1', port)
    serverAddress = ("", port)
    server = HTTPServer(serverAddress, requestHandler)
    print("Started httpserver on port {}".format(port))

    # Wait forever for incoming http requests
    server.serve_forever()
    # protocol     = "HTTP/1.0"


    # SimpleHTTPRequestHandler.protocol_version = Protocol
    # httpd = BaseHTTPServer.HTTPServer(serverAddress, SimpleHTTPRequestHandler)

    # sa = httpd.socket.getsockname()
    # print "Serving HTTP on", sa[0], "port", sa[1], "..."
    # httpd.serve_forever()

if __name__ == '__main__':
    main()
