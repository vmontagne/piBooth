import cv2
from enum import Enum
import numpy as np
from time import sleep, time
from queue import Empty


class DisplayType(Enum):
    VIDEO = "VIDEO"
    WHITE = "WHITE"
    NUMBER = "NUMBER"


SCREEN_HEIGHT = 1024
SCREEN_WIDTH = 1280

SCREEN_RESOLUTION_HEIGHT = 720
SCREEN_RESOLUTION_WIDTH = 1280

PICTURE_HEIGHT = 1536
PICTURE_WIDTH = 1536

PICTURE_RESOLUTION_HEIGHT = 1536
PICTURE_RESOLUTION_WIDTH = 2304

WHITE_FRAME = np.full((SCREEN_HEIGHT, SCREEN_WIDTH, 2), 255, dtype=np.dtype(np.uint8))

STORAGE_PATH = "./data/"


def add_h_line(start, end, y, frame):
    for i in range(start, end):
        frame[y][i][0] = 255
        frame[y][i][1] = 255


def add_v_line(start, end, x, frame):
    for i in range(start, end):
        frame[i][x][0] = 255
        frame[i][x][1] = 255


def add_border(frame):
    begin_width = (SCREEN_WIDTH - SCREEN_HEIGHT) / 2
    end_width = begin_width + SCREEN_HEIGHT
    add_v_line(0, SCREEN_HEIGHT, begin_width, frame)
    add_v_line(0, SCREEN_HEIGHT, begin_width + 1, frame)
    add_v_line(0, SCREEN_HEIGHT, begin_width + 2, frame)
    add_v_line(0, SCREEN_HEIGHT, begin_width + 3, frame)
    add_v_line(0, SCREEN_HEIGHT, end_width, frame)
    add_v_line(0, SCREEN_HEIGHT, end_width - 1, frame)
    add_v_line(0, SCREEN_HEIGHT, end_width - 2, frame)
    add_v_line(0, SCREEN_HEIGHT, end_width - 3, frame)
    add_h_line(begin_width, end_width, 0, frame)
    add_h_line(begin_width, end_width, 1, frame)
    add_h_line(begin_width, end_width, 2, frame)
    add_h_line(begin_width, end_width, 3, frame)
    add_h_line(begin_width, end_width, SCREEN_HEIGHT, frame)
    add_h_line(begin_width, end_width, SCREEN_HEIGHT - 1, frame)
    add_h_line(begin_width, end_width, SCREEN_HEIGHT - 2, frame)
    add_h_line(begin_width, end_width, SCREEN_HEIGHT - 3, frame)


def display_number(cap, fb, number):
    ret, frame = cap.read()
    if not ret:
        sleep(0.01)
        return
    fb.seek(0)
    ratio = SCREEN_RESOLUTION_HEIGHT / SCREEN_HEIGHT
    begin_width = int((SCREEN_RESOLUTION_WIDTH - (SCREEN_RESOLUTION_WIDTH * ratio)) / 2)
    end_width = int(begin_width + (SCREEN_RESOLUTION_WIDTH * ratio))
    resized_frame = cv2.flip(
        cv2.resize(
            frame[0:SCREEN_RESOLUTION_HEIGHT, begin_width:end_width],
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        ),
        1,
    )
    cv2.putText(
        resized_frame,
        str(number),
        (600, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        50,
        (255, 255),
        3,
    )
    frame_bis = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2BGR565)
    add_border(frame=frame_bis)
    fb.write(frame_bis)
    sleep(0.01)


def display_video(cap, fb):
    ret, frame = cap.read()
    if not ret:
        sleep(0.01)
        return
    fb.seek(0)
    ratio = SCREEN_RESOLUTION_HEIGHT / SCREEN_HEIGHT
    begin_width = int((SCREEN_RESOLUTION_WIDTH - (SCREEN_RESOLUTION_WIDTH * ratio)) / 2)
    end_width = int(begin_width + (SCREEN_RESOLUTION_WIDTH * ratio))
    resized_frame = cv2.resize(
        frame[0:SCREEN_RESOLUTION_HEIGHT, begin_width:end_width],
        (SCREEN_WIDTH, SCREEN_HEIGHT),
    )
    frame_bis = cv2.flip(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2BGR565), 1)
    add_border(frame=frame_bis)
    fb.write(frame_bis)
    sleep(0.01)


def display_white_screen(fb):
    fb.seek(0)
    fb.write(WHITE_FRAME)


def take_picture(cap, queue):
    queue.put({"type": DisplayType.NUMBER, "number": 5})
    sleep(1)
    queue.put({"type": DisplayType.NUMBER, "number": 4})
    sleep(1)
    queue.put({"type": DisplayType.NUMBER, "number": 3})
    sleep(1)
    queue.put({"type": DisplayType.NUMBER, "number": 2})
    sleep(1)
    queue.put({"type": DisplayType.NUMBER, "number": 1})
    sleep(1)
    queue.put({"type": DisplayType.WHITE})
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PICTURE_RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, PICTURE_RESOLUTION_WIDTH)
    sleep(0.5)
    ret, frame = cap.read()
    if not ret:
        return

    begin_width = (PICTURE_RESOLUTION_WIDTH - PICTURE_WIDTH) / 2
    end_width = begin_width + PICTURE_WIDTH
    begin_height = (PICTURE_RESOLUTION_HEIGHT - PICTURE_HEIGHT) / 2
    end_height = begin_height + PICTURE_HEIGHT
    cv2.imwrite(
        str(time()) + ".jpg", frame[begin_height:end_height, begin_width, end_width]
    )
    # TODO : display the picture
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_RESOLUTION_WIDTH)
    queue.put({"type": DisplayType.VIDEO})


def display_loop(cap, fb, queue):
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_RESOLUTION_WIDTH)

    display = DisplayType.VIDEO
    number = None

    while True:
        try:
            msg = queue.get_nowait()
            if msg.type == DisplayType.VIDEO:
                display = DisplayType.VIDEO
            elif msg.type == DisplayType.NUMBER:
                display = DisplayType.NUMBER
                number = msg.number
            elif msg.type == DisplayType.WHITE:
                display = DisplayType.WHITE
        except Empty:
            pass

        if display == DisplayType.VIDEO:
            display_video(cap, fb)
        elif display == DisplayType.WHITE:
            display_white_screen(fb)
        elif display == DisplayType.NUMBER:
            display_number(cap, fb, number)
