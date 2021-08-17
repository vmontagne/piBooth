#!/usr/bin/python3.4
# -*-coding:utf-8 -*
import picamera
import time
from PIL import Image, ImageDraw, ImageFont

class Display:
    screenResolution = (2592, 1460)
    # overlayResolution = (1296, 730)
    overlayResolution = (1168, 730)
    pictureResolution = (700, 700)
    color = (255, 255, 255)
    lineWidth = 20
    fontSize = 70
    usbPath = '/var/run/usbmount/Generic_Flash_Disk_1/'
    webPath = '/data/pictures/'

    def __init__(self):
        # Init camera
        camera = picamera.PiCamera()
        camera.resolution = (self.overlayResolution)
        camera.crop = (0.0, 0.0, 1.0, 1.0)
        self.camera = camera
        self.upTop = int((self.overlayResolution[1] - self.pictureResolution[1] - self.lineWidth) / 2) 
        self.upLeft = int((self.overlayResolution[0] - self.pictureResolution[0] - self.lineWidth) / 2) 
        camera.framerate = 24
        camera.start_preview()
        self.cameraOverlay = camera.add_overlay(self.drawOverlay(''), layer=3,
                        alpha=128,
                        format='rgb')

    def drawOverlay(self,text):
        upLeft = self.upLeft
        upTop = self.upTop
        height = self.pictureResolution[1]
        width = self.pictureResolution[0]
        color = self.color
        lineWidth = self.lineWidth
        # img = Image.new("RGB", self.overlayResolution)
        img = Image.new("RGB", (
        ((self.overlayResolution[0] + 31) // 32) * 32,
        ((self.overlayResolution[1] + 15) // 16) * 16,
        ))
        fontpath = 'usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        draw = ImageDraw.Draw(img)
        #ligne haut 
        draw.line((upLeft - lineWidth/2, upTop, upLeft+width + lineWidth/2, upTop), fill=color, width= lineWidth)
        #ligne droite
        draw.line((upLeft+width, upTop - lineWidth/2, upLeft+width, upTop+height + lineWidth/2), fill=color, width= lineWidth)
        #ligne basse
        draw.line((upLeft - lineWidth/2, upTop + height, upLeft+width + lineWidth/2, upTop + height), fill=color, width= lineWidth)
        #ligne gauche
        draw.line((upLeft, upTop - lineWidth/2, upLeft, upTop+height + lineWidth/2), fill=color, width= lineWidth)
        draw.font = ImageFont.truetype(fontpath, self.fontSize, encoding='unic')
        textSize = draw.textsize(text)
        draw.multiline_text(((self.overlayResolution[0]-textSize[0])/2,(self.overlayResolution[1]-textSize[1])/2), text, (255, 255, 255))
        return img.tobytes()

    def drawBlackOverlay(self):
        black = Image.new('RGB',(
                ((self.overlayResolution[0] + 31) // 32) * 32,
                ((self.overlayResolution[1] + 15) // 16) * 16,
            ),
            (255,255,255))
        return black.tobytes()

    def minuterie(self):
        for i in range(5, 0, -1):
            self.cameraOverlay.update(self.drawOverlay(str(i)))
            time.sleep(1)
        self.cameraOverlay.update(self.drawOverlay(''))

    def takePicture(self, fileName):
        file = self.usbPath + fileName
        self.minuterie()
        self.cameraOverlay.alpha = 255
        self.cameraOverlay.update(self.drawBlackOverlay())
        self.camera.stop_preview()
        self.camera.resolution = self.screenResolution
        self.camera.capture(file)
        self.camera.resolution = self.overlayResolution
        self.camera.start_preview()
        im = Image.open(file)
        height = self.pictureResolution[1] * 2
        width = self.pictureResolution[0] * 2
        upTop = int((self.screenResolution[1] - height - self.lineWidth) / 2) 
        upLeft = int((self.screenResolution[0] - width - self.lineWidth) / 2)
        im = im.crop((upLeft, upTop, upLeft+width, upTop+height))
        im.save(file)
        self.cameraOverlay.update(self.pictureOverlay(file))
        #On en registre l'image pour le web
        im.save(self.webPath + fileName)
        time.sleep(5)
        self.cameraOverlay.update(self.drawOverlay(''))
        self.cameraOverlay.alpha = 128


    def pictureOverlay(self, filename):
        black = Image.new('RGB',(
                ((self.overlayResolution[0] + 31) // 32) * 32,
                ((self.overlayResolution[1] + 15) // 16) * 16,
            ),
            (1,1,1))
        picture = Image.open(filename)
        picture.thumbnail(self.pictureResolution)
        black.paste(picture, box=(self.upLeft, self.upTop))
        return black.tobytes()

    def stop(self):
        self.camera.stop_preview()
        self.camera.close()
