import cv2
from Store import Store
from multiprocessing import Process, Queue
from display import display_loop, take_picture
from time import sleep
import RPi.GPIO as GPIO


sleep(20)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


actionPicture = 18
actionPinExit = 3

GPIO.setup(actionPicture, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(actionPinExit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(actionPicture, GPIO.FALLING)
GPIO.add_event_detect(actionPinExit, GPIO.FALLING)

store = Store()
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    fb = open("/dev/fb0", "rb+")

    queue = Queue()
    video = Process(target=display_loop, args=(cap, fb, queue))
    video.start()

    while True:
        if GPIO.event_detected(actionPicture):
            GPIO.remove_event_detect(actionPicture)
            GPIO.remove_event_detect(actionPinExit)
            take_picture(cap, queue)
            GPIO.add_event_detect(actionPicture, GPIO.FALLING)
            GPIO.add_event_detect(actionPinExit, GPIO.FALLING)

    video.join()
