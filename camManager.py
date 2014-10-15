#
#  camManager.py
#  camManager - Raspberry Pi Video Manager
#			Make live updates to the picamera object
#
#  Created by Jeremy Noonan on 10/12/2014

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
	effects = picamera.PiCamera.IMAGE_EFFECTS.keys()

	def __init__(self):
		self.camera = picamera.PiCamera()
		self.camera.resolution = (640,480)
		self.start()

	# Utility functions
	def log(self, message):
		self.camera.annotate_text = message

	def _ycc(self, r, g, b): # in (0,255) range cb = u, cr = v
		y = .299*r + .587*g + .114*b
		cb = 128 -.168736*r -.331364*g + .5*b
		cr = 128 +.5*r - .418688*g - .081312*b
		return int(min(255,y)), int(min(255,cb)), int(min(255, cr))

	def setColor(self, r, g, b): # (r,g,b)
		convertedColor = self._ycc(r, g, b)
		print convertedColor
		self.camera.color_effects = (convertedColor[1], convertedColor[2])

	def setOverlay(self, imagefile):
		# Clear existing overlays
		existingOverlays = self.camera.overlays
		for overlay in existingOverlays:
			self.camera.remove_overlay(overlay)

		# Load the arbitrarily sized image
		img = Image.open(imagefile)
		# Create an image padded to the required size with
		# mode 'RGB'
		pad = Image.new('RGB', (
			((img.size[0] + 31) // 32) * 32,
			((img.size[1] + 15) // 16) * 16,
		))
		# Paste the original image into the padded one
		pad.paste(img, (0, 0))

		# Add the overlay with the padded image as the source,
		# but the original image's dimensions
		o = self.camera.add_overlay(pad.tostring(), size=img.size)
		# By default, the overlay is in layer 0, beneath the
		# preview (which defaults to layer 2). Here we make
		# the new overlay semi-transparent, then move it above
		# the preview
		o.alpha = 128
		o.layer = 3

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

	# Handler
	def handleCommand(self, command):
		print "Handling command"
		print command
		for cmd in command:
			self.log(cmd)
			if cmd == "scan":
				self.scan()
			elif cmd == "colorize":
				newDict = ast.literal_eval(options[0])
				self.log(newDict)
				self.setColor(newDict['r'], newDict['g'], newDict['b'])
			elif cmd == "color":
				self.colorize()
			elif cmd == "exposure":
				self.exposure()
			elif cmd == "effect":
				self.effectize()
			elif cmd == "hflip":
				self.camera.hflip = not self.camera.hflip
			elif cmd == "vflip":
				self.camera.vflip = not self.camera.vflip
			elif cmd == "v1":
				self.setOverlay('images/v1.png')
			elif cmd == "v2":
				self.setOverlay('images/v2.png')
			elif cmd == "v3":
				self.setOverlay('images/v3.png')
			else:
				print "Unknown command: %s" % cmd