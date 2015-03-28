#
#  camManager.py
#  camManager - Raspberry Pi Video Manager
#			Make live updates to the picamera object
#
#  Created by Jeremy Noonan on 10/12/2014

import socket
import time
import ast
import picamera
from PIL import Image

class camManager(object):
	isRunning = False
	quadrants = [(0,0,0.5,0.5), (0.5,0,0.5,0.5), (0.5,0.5,0.5,0.5), (0,0.5,0.5,0.5)]
	sixteenths = [
		(0,0,0.25,0.25), (0,0.25,0.25,0.25), (0,0.5,0.25,0.25), (0,0.75,0.25,0.25),
		(0.25,0,0.25,0.25), (0.25,0.25,0.25,0.25), (0.25,0.5,0.25,0.25), (0.25,0.75,0.25,0.25),
		(0.5,0,0.25,0.25), (0.5,0.25,0.25,0.25), (0.5,0.5,0.25,0.25), (0.5,0.75,0.25,0.25),
		(0.75,0,0.25,0.25), (0.75,0.25,0.25,0.25), (0.75,0.5,0.25,0.25), (0.75,0.75,0.25,0.25)
	]
	exposures = picamera.PiCamera.EXPOSURE_MODES.keys()
	#picamera.PiCamera.IMAGE_EFFECTS.keys()
	effects = ['none', 'negative', 'solarize', 'sketch', 'emboss', 'oilpaint', 'gpen', 'pastel', 'watercolor', 'colorswap', 'washedout', 'cartoon']
	awbmodes = picamera.PiCamera.AWB_MODES.keys()
	server_socket = None
	connection = None
	quiet = False

	def __init__(self):
		self.camera = picamera.PiCamera()
		self.camera.resolution = (720,480)
		self.camera.framerate = 24
		self.readInit()
		self.start()

	# Initialization commands
	def readInit(self):
		f = open('config.txt', 'r')
		for line in f:
			self.handleCommand(self, line)

	# Utility functions
	def log(self, message):
		if self.quiet == False:
			self.camera.annotate_text = str(message)

	def silence(self):
		self.log("");
		self.quiet = True

	def talk(self):
		self.quiet = False
		self.log("logging");

	def _ycc(self, r, g, b): # in (0,255) range cb = u, cr = v
		y = .299*r + .587*g + .114*b
		cb = 128 -.168736*r -.331364*g + .5*b
		cr = 128 +.5*r - .418688*g - .081312*b
		return int(min(255,y)), int(min(255,cb)), int(min(255, cr))

	def setColor(self, r, g, b): # (r,g,b)
		convertedColor = self._ycc(r, g, b)
		print convertedColor
		self.camera.color_effects = (convertedColor[1], convertedColor[2])

	def seteffect(self, effect):
		print "Setting effect to %s" % effect
		self.log(effect)
		self.camera.image_effect = effect

	def setOverlay(self, imagefile):
		self.clearOverlay()

		# Load the arbitrarily sized image
		img = Image.open(imagefile)
		pad = Image.new('RGB', (
			((img.size[0] + 31) // 32) * 32,
			((img.size[1] + 15) // 16) * 16,
		))
		pad.paste(img, (0, 0))
		o = self.camera.add_overlay(pad.tostring(), size=img.size)
		o.alpha = 64
		o.layer = 3

	def clearOverlay(self):
		# Clear existing overlays
		existingOverlays = self.camera.overlays
		for overlay in existingOverlays:
			self.camera.remove_overlay(overlay)

	# Preview manipulation
	def start(self):
		print "Starting..."
		self.isRunning = True
		self.camera.start_preview()

	def stop(self):
		print "Stopping..."
		self.isRunning = False
		self.camera.stop_preview()

	# Commands
	def scan(self):
		print "Scanning"
		for i in range(len(self.quadrants)):
			self.log("Quadrant " + str(i))
			self.camera.zoom = self.quadrants[i]
			time.sleep(2.0)
		for i in range(len(self.sixteenths)):
			self.log("Sixteenth " + str(i))
			self.camera.zoom = self.sixteenths[i]
			time.sleep(2.0)
		self.log("")
		self.camera.zoom = (0,0,1.0,1.0)

	def colorize(self):
		print "Coloring"
		self.log("Red")
		self.setColor(255, 0, 0)
		time.sleep(2.0)
		self.log("Green")
		self.setColor(0, 255, 0)
		time.sleep(2.0)
		self.log("Blue")
		self.setColor(0, 0, 255)
		time.sleep(2.0)
		self.log("")
		self.camera.color_effects = None

	def clearAll(self):
		print "Clear all"
		self.log("")
		self.camera.color_effects = None
		self.camera.image_effect = 'none'	
		self.camera.awb_mode = 'auto'
		self.camera.exposure_mode = 'auto'
		# Clear existing overlays
		existingOverlays = self.camera.overlays
		for overlay in existingOverlays:
			self.camera.remove_overlay(overlay)

	def clearColor(self):
		print "Clearing color"
		self.log("")
		self.camera.color_effects = None

	def effectize(self):
		print "Setting effect"
		currentEffect = self.camera.image_effect
		nextIndex = self.effects.index(currentEffect) + 1
		if nextIndex >= len(self.effects):
			nextIndex = 0
		nextEffect = self.effects[nextIndex]
		self.log(nextEffect)
		self.camera.image_effect = nextEffect

	def exposure(self):
		print "Setting exposure"
		currentExposure = self.camera.exposure_mode
		nextIndex = self.exposures.index(currentExposure) + 1
		if nextIndex >= len(self.exposures):
			nextIndex = 0
		nextExposure = self.exposures[nextIndex]
		self.log(nextExposure)
		self.camera.exposure_mode = nextExposure

	def awbmode(self):
		print "Setting awb mode"
		currentMode = self.camera.awb_mode
		nextIndex = self.awbmodes.index(currentMode) + 1
		if nextIndex >= len(self.awbmodes):
			nextIndex = 0
		nextMode = self.awbmodes[nextIndex]
		self.log(nextMode)
		self.camera.awb_mode = nextMode

	def streamit(self):
		serverPort = 8000
		print "Starting stream on port %s" % serverPort
		self.server_socket = socket.socket()
		self.server_socket.bind(('0.0.0.0', 8000))
		self.server_socket.listen(0)
		# Accept a single connection and make a file-like object out of it
		self.connection = self.server_socket.accept()[0].makefile('wb')
		try:
			self.camera.start_recording(self.connection, format='h264')
			self.camera.wait_recording(0)
		except:
			print "Exception"
			self.connection.close()
			self.server_socket.close()

	def stopstream(self):
		print "Stopping stream"
		self.camera.stop_recording()
		self.connection.close()
		self.server_socket.close()

	# Handler
	def handleCommand(self, command):
		print "Handling command"
		print command
		for cmd in command:
			self.log(cmd)
			if cmd == "scan":
				self.scan()
			elif cmd == "stream":
				self.streamit()
			elif cmd == "stopstream":
				self.stopstream();
			elif cmd == "zoom":
				zoomDict = ast.literal_eval(command[cmd][0])
				self.log(zoomDict)
				self.camera.zoom = (zoomDict['x'], zoomDict['y'], zoomDict['w'], zoomDict['h'])
			elif cmd == "colorize":
				newDict = ast.literal_eval(command[cmd][0])
				self.log(newDict)
				self.setColor(newDict['r'], newDict['g'], newDict['b'])
			elif cmd == "color":
				self.colorize()
			elif cmd == "clearcolor":
				self.clearColor();
			elif cmd == "clearall":
				self.clearAll();
			elif cmd == "exposure":
				self.exposure()
			elif cmd == "effect":
				self.effectize()
			elif cmd == "seteffect":
				self.seteffect(command[cmd][0]);
			elif cmd == "awbmode":
				self.awbmode();
			elif cmd == "hflip":
				self.camera.hflip = not self.camera.hflip
			elif cmd == "vflip":
				self.camera.vflip = not self.camera.vflip
			elif cmd == "clear":
				self.clearOverlay()
			elif cmd == "v1":
				self.setOverlay('images/v1.png')
			elif cmd == "v2":
				self.setOverlay('images/v2.png')
			elif cmd == "v3":
				self.setOverlay('images/v3.png')
			elif cmd == "silence":
				self.silence();
			elif cmd == "talk":
				self.talk();
			else:
				print "Unknown command: %s" % cmd