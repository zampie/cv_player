from src.mediapipe_api import *
from src.cv_player_gui import CVPlayerGUI as CVPlayer
# from cv_player import CVPlayer
from functools import partial


pre_process = partial(cv2.resize, dsize=(960, 540))
# preprocess = None

# model = HandDetector()
model = PoseDetector()
# model = FaceMesh()

player = CVPlayer(pre_process=pre_process, process=model.run, show_scare=1)

# player.play_video_folder(r"E:\Videos\Anime\[SweetSub&VCB-Studio] Flip Flappers [Ma10p_1080p]")
player.play_screen()
# player.play_camera()
# player.play_img_folder(r"D:\Illustrations")
