#
#  camManager.py
#  camManager - Raspberry Pi Video Manager
#			Make live updates to the picamera object
#
#  Created by Jeremy Noonan on 10/12/2014

import time
import picamera

class camManager(object):
	isRunning = False
	quadrants = [(0,0,0.5,0.5), (0.5,0,0.5,0.5), (0.5,0.5,0.5,0.5), (0,0.5,0.5,0.5)]
	triplets = [(0,0,1,0.33), (0,0.33,0,0.33), (0,0.66,0,0.33)]

	def __init__(self):
		self.camera = picamera.PiCamera()
		self.start()

	# Utility functions
	def log(self, message):
		self.camera.annotate_text = message

	def _ycc(r, g, b): # in (0,255) range cb = u, cr = v
		y = .299*r + .587*g + .114*b
		cb = 128 -.168736*r -.331364*g + .5*b
		cr = 128 +.5*r - .418688*g - .081312*b
		return y, cb, cr

	def setColor(r, g, b): # (r,g,b)
		convertedColor = self._ycc(r, g, b)
		self.camera.color_effects = (convertedColor[1], convertedColor[2])

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
		for i in range(len(quadrants)):
			self.log("Quadrant %" % i)
			self.camera.zoom = self.quadrants[i]
			time.sleep(2.0)
		for i in range(len(triplets)):
			self.log("Triplet %" % i)
			self.camera.zoom = self.triplets[i]
			time.sleep(2.0)
		self.log("")
		self.camera.zoom = (0,0,1,1)

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

	def exposure(self):
		print "Setting exposure"
		currentExposure = self.camera.exposure_mode
		nextIndex = picamera.PiCamera.EXPOSURE_MODES.index(currentExposure) + 1
		if nextIndex >= len(picamera.PiCamera.EXPOSURE_MODES):
			nextIndex = 0
		nextExposure = picamera.PiCamera.EXPOSURE_MODES[nextIndex]
		self.log(nextExposure)
		self.camera.exposure_mode = nextExposure

	# Handler
	def handleCommand(self, command):
		print "Handling command"
		print command
		for cmd in command:
			self.log(cmd)
			if cmd == "scan":
				self.scan()
			elif cmd == "color":
				self.colorize()
			elif cmd == "exposure":
				self.exposure()
			elif cmd == "hflip":
				self.camera.hflip = not self.camera.hflip
			elif cmd == "vflip":
				self.camera.vflip = not self.camera.vflip
			else:
				print "Unknown command: %s" % cmd