from cv_player import CVPlayer
from utils import *
from functools import partial

if __name__ == '__main__':
    with ContextTimer("player", "min"):

        player = CVPlayer(window_name="cv player",  # 窗口名
                          save_path="./capture",  # 保存路径
                          visible=True,  # 窗口是否可见，False时为静默模式，此时不接受键鼠输入
                          show_scare=1,  # 显示窗口的大小
                          save_img=False,  # 是否切帧
                          save_video=False,  # 是否保存视频
                          frame_stride=1,  # 帧的跨度
                          preprocessing_fun=None,  # 前处理函数的函数指针，建议进行resize或padding等操作
                          processing_fun=None,  # 图片处理函数的函数指针，建议进行绘图操作，不支持改变图片大小
                          show_fps=True,  # 是否显示fps
                          frame_sync=True,  # 是否限制最大帧率
                          save_suffix="_out")  # 输出切帧文件的后缀名，仅在有图片处理函数时才启用

        # player.preprocessing_fun = padding_to_square  # 设置图片处理函数
        # player.processing_fun = draw_rect  # 设置图片处理函数，请确保只有一个img参数

        player.play_screen()
        # player.play_folder(r"E:\Videos\Anime")
        # player.play(r"E:\Videos\Anime\[VCB-Studio] To Love-Ru Trouble [Ma10p_1080p]\
        #             [VCB-Studio] To Love-Ru Trouble [01][Ma10p_1080p][x265_flac_aac].mkv")
        # player.play(0)
        # player.play_img_folder(r"your_img_folder", pause=True, fps=1)
        # ......
