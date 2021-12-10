import sys
import time

import cv2
import numpy as np
from PIL import ImageGrab
from utils import *
from cv_player import CVPlayer


class CVPlayerGUI(CVPlayer):
    def __init__(self):
        super(CVPlayerGUI, self).__init__(visible=True)
        self.auto_set_bat = False

    def play_video(self, source):
        print("open: ", source)
        self.source = source
        self.cap = cv2.VideoCapture(source)

        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.ori_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.target_fps = self.ori_fps

        print("w: %d, h: %d, fps: %.2f, total frames: %d" %
              (self.w, self.h, self.ori_fps, self.total_frames))

        if self.total_frames == 0:
            return

        self.update_size_by_preprocessing_fun()
        self.writer_init()

        cv2.namedWindow(self.window_name)
        cv2.resizeWindow(self.window_name, int(self.w * self.show_scare), int(self.h * self.show_scare))
        cv2.setMouseCallback(self.window_name, self.call_mouse, param=self.frame_id)
        cv2.createTrackbar("pos", self.window_name, 0, self.total_frames - 1, self.call_pos_bar)

        # cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # cv2.setTrackbarMin("pos", self.window_name, 0)
        # cv2.setTrackbarMax("pos", self.window_name, self.total_frames - 1)

        self.auto_set_bat = True
        cv2.setTrackbarPos("pos", self.window_name, 0)
        self.auto_set_bat = False

        self.frame_id = -1
        clock = Clock()
        while self.cap.isOpened() and not self.exit_flag and not self.skip_flag:
            self.frame_id += 1
            # print("frame id: ", self.frame_id)

            # 防止回调函数执行
            self.auto_set_bat = True
            cv2.setTrackbarPos("pos", self.window_name, self.frame_id)
            # cv2.setTrackbarPos("pos", self.window_name, 50)
            self.auto_set_bat = False
            ret, self.frame = self.cap.read()
            if not ret:
                print("not ret")
                break
            if self.frame_id % self.frame_stride != 0:
                continue
            if self.frame_id == self.total_frames - 1:
                self.pause = True

            self.frame_show()
            self.wait_key(int(not self.pause))

            clock.update()
            clock.fps_sync(self.target_fps if self.frame_sync else 0)
            # print('avg fps: ', clock.avg_fps)
            self.avg_fps = clock.avg_fps
            self.instant_fps = clock.instant_fps

            while self.pause:
                self.update_frame()
                self.wait_key(1)

        print("release: ", source)
        self.file_id += 1
        self.cap.release()
        self.writer_release()
        cv2.destroyAllWindows()

    def call_pos_bar(self, pos):
        if self.auto_set_bat:
            # print("auto update bar")
            return
        print("call bar pos:", pos)
        self.frame_id = pos
        if self.frame_id < self.total_frames - 1:
            print("bar call update")
            self.update_frame()
        else:
            print("bar pause")
            self.pause = True

    def update_frame(self):
        if not self.cap:
            return
        # print("set frame at: ", self.frame_id)
        self.frame_id = max(0, self.frame_id)
        self.frame_id = min(self.frame_id, self.total_frames - 1)
        # print("update frame at: ", self.frame_id)

        self.auto_set_bat = True
        cv2.setTrackbarPos("pos", self.window_name, self.frame_id)
        self.auto_set_bat = False

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_id)
        ret, self.frame = self.cap.read()
        if not ret:
            print("update frame field")
            return
        self.frame_show()


if __name__ == '__main__':
    player = CVPlayerGUI()
    player.show_scare = 1
    player.play_video_folder(r"E:\Videos\Anime")
