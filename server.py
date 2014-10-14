#!/usr/bin/env python
#
#  WebCamServer.py
#  WebCamServer - Raspberry Pi Video Wall WebController
#
#  Created by Jeremy Noonan on 10/12/2014

import SimpleHTTPServer, SocketServer
import urlparse
import camManager

PORT = 8080 # Change this if you wish to listen on a different port

class WebController (SimpleHTTPServer.SimpleHTTPRequestHandler):
  mgr = camManager.camManager()

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
    self.mgr.handleCommand(query);

httpd = SocketServer.TCPServer(("", PORT), WebController)

print "WebCamServer -- Listening on port", PORT

httpd.serve_forever()