from Display import Display
from Store import Store
import time
import RPi.GPIO as GPIO

time.sleep(20)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def takePicture():
    filename = str(time.time()) + '.jpg'
    display.takePicture(filename)
    store.addFile(filename)


actionPicture = 18
actionPinExit = 3

GPIO.setup(actionPicture, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(actionPinExit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(actionPicture, GPIO.FALLING)
GPIO.add_event_detect(actionPinExit, GPIO.FALLING)

display = Display()
store = Store()
exitFlag = False

def switchExitFlag():
    global exitFlag
    exitFlag = True

while not exitFlag:
    if GPIO.event_detected(actionPicture):
        GPIO.remove_event_detect(actionPicture)
        GPIO.remove_event_detect(actionPinExit)
        takePicture()
        GPIO.add_event_detect(actionPicture, GPIO.FALLING)
        GPIO.add_event_detect(actionPinExit, GPIO.FALLING)
    if GPIO.event_detected(actionPinExit):
        switchExitFlag()
        