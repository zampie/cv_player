import sys
import time

import cv2
import numpy as np
from PIL import ImageGrab
from src.utils import *


class CVPlayer:
    def __init__(self,
                 window_name="cv player",
                 save_path="./capture",
                 visible=True,
                 show_scare=0.5,
                 save_img=False,
                 save_video=False,
                 frame_stride=1,
                 pre_process=None,
                 process=None,
                 show_fps=True,
                 frame_sync=False,
                 save_suffix="_out"):

        self.window_name = window_name
        self.save_path = save_path
        self.visible = visible
        self.show_scare = show_scare
        self.save_img = save_img
        self.save_video = save_video
        self.frame_stride = frame_stride
        self.pre_process = pre_process
        self.process = process
        self.show_fps = show_fps
        self.frame_sync = frame_sync
        self.save_suffix = save_suffix

        self.source = ''
        self.save_name = ''
        self.pause = False
        self.cap = None
        self.writer = None
        self.frame = None
        self.ori_fps = 15
        self.target_fps = self.ori_fps
        self.frame_time = 1e-13
        self.avg_fps = 0
        self.instant_fps = 0
        self.frame_num = -1
        self.total_frames = 0
        self.file_id = 0
        self.w = 0
        self.h = 0
        self.delay = 0
        self.exit_flag = False
        self.skip_flag = False
        makedir(self.save_path)

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

        if self.ori_fps == 0:
            return

        self.update_size_by_preprocessing_fun()
        self.writer_init()

        cv2.namedWindow(self.window_name)
        cv2.resizeWindow(self.window_name, int(self.w * self.show_scare), int(self.h * self.show_scare))
        cv2.setMouseCallback(self.window_name, self.call_mouse, param=self.frame_num)

        self.frame_num = -1
        clock = Clock()
        while self.cap.isOpened() and not self.exit_flag and not self.skip_flag:
            self.frame_num += 1

            ret, self.frame = self.cap.read()
            if not ret:
                print("video get frame field, break")
                break
            if self.frame_num % self.frame_stride != 0:
                continue

            self.frame_show()
            self.wait_key(int(not self.pause))
            clock.update()
            clock.fps_sync(self.target_fps if self.frame_sync else 0)
            # print('avg fps: ', clock.avg_fps)
            self.avg_fps = clock.avg_fps
            self.instant_fps = clock.instant_fps

            while self.pause:
                self.wait_key(0)

        self.file_id += 1
        self.cap.release()
        self.writer_release()

    def play_camera(self, source=0, w=1920, h=1080):
        print("open: ", source)
        self.source = 'camera'
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))

        self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.ori_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print("w: %d, h: %d, fps: %.2f, total frames: %d" %
              (self.w, self.h, self.ori_fps, self.total_frames))

        self.update_size_by_preprocessing_fun()
        self.writer_init()

        clock = Clock()
        while self.cap.isOpened() and not self.exit_flag:
            self.frame_num += 1
            ret, self.frame = self.cap.read()
            if not ret:
                print("camera get frame field, retry...")
                continue
            if self.frame_num % self.frame_stride != 0:
                continue
            self.frame_show()
            self.wait_key(int(not self.pause))
            clock.update()
            clock.fps_sync(self.target_fps if self.frame_sync else 0)
            self.avg_fps = clock.avg_fps
            self.instant_fps = clock.instant_fps

        self.cap.release()
        self.writer_release()

    def play_video_folder(self, folder):
        file_names = read_files(folder)
        for file_name in file_names:
            self.play_video(file_name)
            if self.skip_flag:
                self.skip_flag = False
                continue

            if self.exit_flag:
                break

    def play_screen(self, bbox=None):
        print("cap_screen: ")
        self.frame_stride = 1
        self.source = "screen"
        frame = ImageGrab.grab(bbox=bbox)
        print("screen size: ", frame.size)
        self.w, self.h = frame.size
        self.update_size_by_preprocessing_fun()
        self.writer_init()

        clock = Clock()
        while not self.exit_flag:
            self.frame_num += 1
            self.frame = pil_to_cv(ImageGrab.grab(bbox=bbox))
            self.frame_show()
            self.wait_key(int(not self.pause))
            clock.update()
            clock.fps_sync(self.target_fps if self.frame_sync else 0)
            self.avg_fps = clock.avg_fps
            self.instant_fps = clock.instant_fps

    def play_img(self, file_name):
        try:
            print("open: ", file_name)
            self.source = file_name
            self.frame_num += 1
            self.frame = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), cv2.IMREAD_COLOR)
            # self.frame = cv2.imread(file_name)
            self.frame_show()
            self.wait_key(int(not self.pause))
            self.file_id += 1

        except Exception as e:
            print("field to open: ", file_name)
            print("error: ", e)

    def play_img_folder(self, folder, pause=True, fps=1):
        self.ori_fps = fps
        self.frame_stride = 1
        self.pause = pause

        file_names = read_files(folder, ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG', 'bmp', 'BMP'])
        # file_names = read_files(folder)
        clock = Clock()
        for file_name in file_names:
            self.play_img(file_name)
            if self.exit_flag:
                break
            clock.update()
            clock.fps_sync(self.target_fps if self.frame_sync else 0)
            self.avg_fps = clock.avg_fps
            self.instant_fps = clock.instant_fps

    def frame_show(self):
        # sub_filename = os.path.splitext(self.file_name.split("\\")[-1])[0]
        # self.save_name = os.path.join(self.save_path, sub_filename + '_' + str(self.frame_id).zfill(8))
        if self.cap:
            self.save_name = os.path.join(self.save_path, str(self.file_id) + '_' + str(self.frame_num).zfill(8))
        else:
            self.save_name = os.path.join(self.save_path, str(self.frame_num).zfill(8))

        if self.pre_process:
            self.frame = self.pre_process(self.frame)

        if self.save_img:
            cv2.imwrite(self.save_name + ".jpg", self.frame)

        if self.process:
            self.frame = self.process(self.frame)
            if self.save_img:
                cv2.imwrite(self.save_name + self.save_suffix + ".jpg", self.frame)

        if self.save_video:
            print('write frame num: ', self.frame_num)
            self.writer.write(self.frame)

        if self.visible:
            # show_frame： 打上文字， 调整尺寸， 显示的帧
            show_size = (int(self.frame.shape[1] * self.show_scare), int(self.frame.shape[0] * self.show_scare))
            show_frame = cv2.resize(self.frame, show_size)
            if self.show_fps:
                self.put_text(show_frame)
            cv2.imshow(self.window_name, show_frame)

    # @timer("ms")
    def wait_key(self, delay):
        if not self.visible:
            return
        # print("cv2.waitKey(%d)" % delay)
        key = chr(cv2.waitKey(delay) & 0xFF)
        if key == ' ':
            self.pause = not self.pause
            print("pause: ", self.pause)
        if key == 'x':
            print("capture: ", self.frame_num)
            cv2.imwrite(self.save_name + "_cap.jpg", self.frame)
        if key == 't':
            self.show_fps = not self.show_fps
            print("save img: ", self.show_fps)
        if key == 's':
            self.save_img = not self.save_img
            print("save img: ", self.save_img)
        if key == 'c':
            self.frame_sync = not self.frame_sync
            print("frame_sync: ", self.frame_sync)
        # 没有writer时，不接受录屏
        if key == 'r' and self.writer:
            self.save_video = not self.save_video
            print("recoding: ", self.save_video)
        # 保存并新建视频分段
        if key == 'n' and self.writer:
            self.writer_release()
            self.writer_init()
        if key == 'u':
            # self.frame_stride //= 2
            # self.frame_stride = max(self.frame_stride, 1)
            # print("speed down: ", self.frame_stride)
            self.target_fps = int(max(self.target_fps - 1, 1) + 0.5)
            print("speed down: ", self.target_fps)
        if key == 'i':
            # self.frame_stride *= 2
            # self.frame_stride = min(self.frame_stride, 128)
            # print("speed up: ", self.frame_stride)
            self.target_fps = int(self.target_fps + 1 + 0.5)
            print("speed up: ", self.target_fps)
        if key == 'o':
            self.target_fps = self.ori_fps
            print("reset fps: ", self.target_fps)
        if key == 'd' and self.cap:
            self.frame_num = self.frame_num - 1
            print("reset frame at: ", self.frame_num)
            self.pause = True
            self.update_frame()
        if key == 'f' and self.cap:
            self.frame_num = self.frame_num + 1
            print("reset frame at: ", self.frame_num)
            self.pause = True
            self.update_frame()
        if key == 'D' and self.cap:
            self.frame_num = self.frame_num - 100
            print("reset frame at: ", self.frame_num)
            self.pause = True
            self.update_frame()
        if key == 'F' and self.cap:
            self.frame_num = self.frame_num + 100
            print("reset frame at: ", self.frame_num)
            self.pause = True
            self.update_frame()
        if key == '\r':
            self.pause = False
            self.skip_flag = True

        if key == '\x1b' or not cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE):
            print("esc")
            self.pause = False
            self.exit_flag = True

    def update_frame(self):
        if not self.cap:
            return
        # print("set frame at: ", self.frame_id)
        self.frame_num = max(0, self.frame_num)
        self.frame_num = min(self.frame_num, self.total_frames - 1)
        print("update frame at: ", self.frame_num)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
        ret, self.frame = self.cap.read()
        if not ret:
            print("update frame field")
            return
        self.frame_show()

    # @timer("ms")
    def writer_init(self, code="mp4v", type=".mp4"):
        # def writer_init(self, code="xvid", type=".avi"):
        # 静默模式中，不能中途开关，不执行清理函数，防止残生临时文件，如要录像，必须在一开始就打开开关,并等待程序正常结束
        # xvid支持不完整文件但时间信息不全， mp4v不能播放
        if not self.visible and not self.save_video:
            return

        codec = cv2.VideoWriter_fourcc(*code)
        # time_st = time.gmtime()
        # self.video_name = str(time_st.tm_year) + "_" + str(time_st.tm_mon) + "_" + str(time_st.tm_mday) + "_" + str(
        #     time_st.tm_hour + 8) + "_" + str(time_st.tm_min) + "_" + str(time_st.tm_sec) + type

        self.video_name = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + type
        self.video_name = os.path.join(self.save_path, self.video_name)

        self.writer = cv2.VideoWriter(self.video_name, codec, self.ori_fps, (self.w, self.h))
        print("record video at: " + self.video_name)

    def update_size_by_preprocessing_fun(self):
        if self.pre_process:
            self.h, self.w, _ = cal_new_size((self.h, self.w, 3), self.pre_process)

    def writer_release(self):
        if self.writer:
            self.writer.release()
            if os.path.isfile(self.video_name):
                video_size = os.path.getsize(self.video_name)
                print("video size: %d byte" % video_size)
                if video_size < 1024:
                    print("del useless video cache: ", self.video_name)
                    os.remove(self.video_name)
                else:
                    print("save video: ", self.video_name)

    def put_text(self, show_frame):
        out_text = ""
        out_text += "avg fps: %d " % self.avg_fps
        out_text += "instant fps: %d " % self.instant_fps
        out_text += "id: " + str(self.frame_num) + " "
        color = [0, 200, 0]
        if self.save_video:
            color[1] = 0
            color[2] = 200
        if self.save_img:
            color[0] = 200
            color[1] = 0

        cv2.putText(show_frame, out_text, (20, 40), cv2.FONT_HERSHEY_TRIPLEX, 1, color, 1)

    def call_mouse(self, event, x, y, flag, param):
        if event != 0:
            # print(event)
            if event == cv2.EVENT_LBUTTONDOWN:
                print("frame: ", self.frame_num, "position: %d, %d" % (x, y))
            if event == cv2.EVENT_LBUTTONDBLCLK:
                self.pause = not self.pause
                print("pause: ", self.pause)
            if event == cv2.EVENT_RBUTTONDOWN:
                print("capture: ", self.frame_num)
                cv2.imwrite(self.save_name + "_cap.jpg", self.frame)


if __name__ == '__main__':
    player = CVPlayer()
    player.play_video_folder(r"E:\Videos\Anime\[SweetSub&VCB-Studio] Flip Flappers [Ma10p_1080p]")
    # player.play_img_folder(r"D:\Illustrations")
