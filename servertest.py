#!/usr/bin/env python
#
#  WebCamServer.py
#  WebCamServer - Raspberry Pi Video Wall WebController
#
#  Created by Jeremy Noonan on 10/12/2014

import SimpleHTTPServer, SocketServer
import urlparse
import ast

PORT = 9080 # Change this if you wish to listen on a different port

class WebController (SimpleHTTPServer.SimpleHTTPRequestHandler):

  def do_GET(self):
    # Parse query data
    parsedParams = urlparse.urlparse(self.path)
    queryParsed = urlparse.parse_qs(parsedParams.query)

    # Add 'api' prefix to URL to perform commands
    if parsedParams.path == "/api":
      self.processRequest(queryParsed)
    else:
      # Default to serve up a local file 
      SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self);

  def processRequest(self, query):
    # Send response then handle so we don't keep the browser waiting
    self.send_response(200)
    print query
    for cmd in query:
      print(cmd)
      options = query[cmd]
      print options[0]
      newDict = ast.literal_eval(options[0])
      print newDict
      print newDict['r']
      print newDict['g']
      print newDict['b']

httpd = SocketServer.TCPServer(("", PORT), WebController)

print "WebCamServer -- Listening on port", PORT

httpd.serve_forever()