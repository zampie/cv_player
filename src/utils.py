import os
import time
from functools import wraps
from collections import Iterable, deque

import numpy as np
import cv2

EPS = 1e-15


def makedir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def read_files(path, types=None):
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if types:
                type = filename.split('.')[-1]
                # type = os.path.splitext(filename)[1]
                # print(type)
                if type in types:
                    yield os.path.join(root, filename)
                    continue
            else:
                yield os.path.join(root, filename)


def centre_crop(img, size):
    h, w, c = img.shape

    if isinstance(size, Iterable):
        size_x, size_y = size
    else:
        size_x = size_y = size

    size_x = min(size_x, w)
    size_y = min(size_y, h)

    c_x = w // 2
    c_y = h // 2

    x0 = c_x - size_x // 2
    x1 = x0 + size_x

    y0 = c_y - size_y // 2
    y1 = y0 + size_y

    return img[y0:y1, x0:x1]


def crop_to_square(img):
    h, w, c = img.shape
    return centre_crop(img, min(h, w))


def crop_rect(img, rect):
    x0, y0, x1, y1 = rect
    return img[y0:y1, x0:x1, :]


def draw_rect(img, rect=(0, 0, 200, 200), color=(0, 0, 255)):
    x0, y0, x1, y1 = rect
    cv2.rectangle(img, (x0, y0), (x1, y1), color, 3)
    return img


def move_rect(rect, move):
    x_move = move[0]
    y_move = move[1]
    ret_rect = [rect[0] + x_move, rect[1] + y_move, rect[2] + x_move, rect[3] + y_move]
    return ret_rect


def cal_area(rect):
    x0, y0, x1, y1 = rect
    w = x1 - x0
    h = y1 - y0
    return w * h


def cal_iou(rect0, rect1):
    left0, top0, right0, bottom0 = rect0
    left1, top1, right1, bottom1 = rect1

    area0 = (right0 - left0) * (bottom0 - top0)
    area1 = (right1 - left1) * (bottom1 - top1)

    in_w = min(right0, right1) - max(left0, left1)
    in_h = min(bottom0, bottom1) - max(top0, top1)

    inter = 0 if in_h < 0 or in_w < 0 else in_w * in_h

    union = area0 + area1 - inter

    iou = inter / union

    return iou


def padding_to_square(img):
    h, w, c = img.shape
    left, right, top, bottom = 0, 0, 0, 0

    if w == h:
        return img
    elif w > h:
        over = w - h
        top = over // 2
        bottom = over - top
    else:
        over = h - w
        left = over // 2
        right = over - left

    return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, (0, 0, 0))


def pil_to_cv(img):
    out_img = np.array(img)
    out_img = cv2.cvtColor(out_img, cv2.COLOR_RGB2BGR)
    return out_img


def cal_new_size(shape, fun):
    demi_img = np.ones(shape)
    return fun(demi_img).shape


def decorator_timer(timer_unit="ms"):
    def timer(fun):
        # print(fun.__name__ + " timer: init")
        @wraps(fun)
        def wrapper(*args, **kwargs):

            print("args: ", args)
            time_str = time.time()

            print(fun.__name__, ": start")
            res = fun(*args, **kwargs)

            time_cost = time.time() - time_str
            unit = timer_unit
            if unit == "ms":
                time_cost = time_cost * 1000
            elif unit == "min":
                time_cost = time_cost / 60
            elif unit == "h":
                time_cost = time_cost / 3600
            else:
                unit = "s"

            print(fun.__name__ + " cost: %.3f " % time_cost + unit)
            return res

        return wrapper

    return timer


class ContextTimer:
    def __init__(self, name="timer", unit="ms"):
        self.name = name
        self.unit = unit
        # print(self.name + ": timer init")

    def __enter__(self):
        print(self.name + ": timer start")
        self.time_str = time.time()
        return self.time_str

    def __exit__(self, exc_type, exc_val, exc_tb):
        time_cost = time.time() - self.time_str

        if self.unit == "ms":
            time_cost = time_cost * 1000
        elif self.unit == "min":
            time_cost = time_cost / 60
        elif self.unit == "h":
            time_cost = time_cost / 3600
        else:
            self.unit = "s"

        print(self.name + " cost: %.2f " % time_cost + self.unit)
        # 返回True会导致程序不能退出
        # return True


def avg(arr):
    arr_size = len(arr)
    arr_sum = sum(arr)
    return 0 if arr_size == 0 else arr_sum / arr_size


class Clock:
    def __init__(self, fps_win_len=30):
        self.frame_time = 0
        self.frame_time_queue = deque(maxlen=fps_win_len)
        self.avg_frame_time = 0

        self.avg_fps = 0
        self.instant_fps = 0

        self.start_time = time.time()

    def update(self):
        end_time = time.time()
        self.frame_time = end_time - self.start_time
        self.start_time = time.time()
        self.frame_time_queue.append(self.frame_time)
        self.avg_frame_time = avg(self.frame_time_queue)

        self.instant_fps = 1 / (self.frame_time + EPS)
        self.avg_fps = 1 / (self.avg_frame_time + EPS)

    def fps_sync(self, target_fps):
        if target_fps <= 0:
            return

        target_frame_time = 1 / target_fps
        sleep_time = target_frame_time - self.avg_frame_time
        if sleep_time > 0:
            # print('sleep_time: ', sleep_time)
            time.sleep(sleep_time)


if __name__ == '__main__':
    file_name = "1.jpg"
    img = cv2.imread(file_name)
    print(img.shape)

    # img = centre_crop(img, (200, 400))
    img = padding_to_square(img)

    cv2.imshow(__file__, img)
    print(img.shape)

    cv2.waitKey(0)
