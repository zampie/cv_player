import os
import multiprocessing
import tkinter
from tkinter import filedialog, messagebox

import windnd
from src.cv_player_gui import CVPlayerGUI
from src.mediapipe_api import PoseDetector


def player_init():
    paras = {"show_fps": False, "frame_sync": True}
    # paras["process"] = PoseDetector().run
    player = CVPlayerGUI(**paras)
    return player


def player_selector(source, mode):
    print('process start : ', end=" ")
    print('pid : ', os.getpid())

    player = player_init()

    if mode == "image_folder":
        player.play_img_folder(source)
    elif source == "screen":
        player.play_screen()
    elif source == "camera":
        player.play_camera()
    else:
        player.play(source)

    print('process over : ', end=" ")
    print('pid : ', os.getpid())


def multiprocess_launch(source, mode=None):
    play_thread = multiprocessing.Process(target=player_selector, args=(source, mode))
    # play_thread = PlayerSelector(source, mode, g_paras)
    play_thread.daemon = True
    play_thread.start()


class Launcher:
    def __init__(self):
        self.window = tkinter.Tk()

        self.window.title("player console")
        self.window.geometry("400x400")
        self.window.iconbitmap(__file__)

        windnd.hook_dropfiles(self.window, func=self.drop_event)

        menu_bar = tkinter.Menu(self.window)
        file_menu = tkinter.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='exit', command=self.window.quit)

        help_menu = tkinter.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='help', command=self.show_help)
        help_menu.add_separator()
        help_menu.add_command(label='copy right', command=self.show_copy_right)

        menu_bar.add_cascade(label='file', menu=file_menu)
        menu_bar.add_cascade(label='help', menu=help_menu)
        self.window.config(menu=menu_bar)

        open_file_button = tkinter.Button(self.window, text='open file', command=self.open_file_event)
        open_file_button.pack()

        open_video_folder_button = tkinter.Button(self.window, text='open video folder',
                                                  command=self.open_video_folder_event)
        open_video_folder_button.pack()

        open_image_folder_button = tkinter.Button(self.window, text='open image folder',
                                                  command=self.open_image_folder_event)
        open_image_folder_button.pack()

        open_camera_button = tkinter.Button(self.window, text='open camera', command=self.open_camera_event)
        open_camera_button.pack()

        screen_capture_button = tkinter.Button(self.window, text='screen capture', command=self.screen_capture_event)
        screen_capture_button.pack()

        text_label = tkinter.Label(self.window, text="\n\n\n\n\ndraw to play")
        text_label.pack()

    @staticmethod
    def drop_event(binary_files):
        file_list = []
        for file in binary_files:
            file_list.append(file.decode('gbk'))

        print(file_list)
        multiprocess_launch(file_list[0])

    @staticmethod
    def open_file_event():
        file = filedialog.askopenfilename()
        print(file)
        if file:
            multiprocess_launch(file)

    @staticmethod
    def open_video_folder_event():
        dir = filedialog.askdirectory()
        print(dir)
        if dir:
            multiprocess_launch(dir)

    @staticmethod
    def open_image_folder_event():
        dir = filedialog.askdirectory()
        print(dir)
        if dir:
            multiprocess_launch(dir, mode="image_folder")

    @staticmethod
    def open_camera_event():
        multiprocess_launch(0)

    @staticmethod
    def screen_capture_event():
        multiprocess_launch("screen")

    @staticmethod
    def show_help():
        tkinter.messagebox.showinfo('help', 'no help')

    @staticmethod
    def show_copy_right():
        tkinter.messagebox.showinfo('copy right', 'made by zampie\nconnect me : zampielzp@gmail.com')

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    Launcher().run()
