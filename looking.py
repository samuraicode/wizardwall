import time
import picamera

with picamera.PiCamera() as camera:
    camera.start_preview()
    try:
        for i in range(4):
            xy = (i - 1) * 0.25
            camera.zoom = (xy, xy, 0.25, 0.25)
            time.sleep(2.0)
    finally:
        camera.stop_preview()
