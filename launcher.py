from src.cv_player_gui import CVPlayerGUI
import tkinter
from tkinter import filedialog, messagebox
from src.mediapipe_api import PoseDetector

import windnd
import threading
import multiprocessing

import os


def player_init():
    paras = {"show_fps": False}
    # paras["process"] = PoseDetector().run
    player = CVPlayerGUI(**paras)
    return player


def multiprocess_launch(source, mode=None):
    play_thread = multiprocessing.Process(target=player_selector, args=(source, mode))
    # play_thread = PlayerSelector(source, mode, g_paras)
    play_thread.daemon = True
    play_thread.start()


def player_selector(source, mode):
    print('process start : ', end=" ")
    print('thread name: ', threading.currentThread().getName(), end=" ")
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
    print('thread name: ', threading.currentThread().getName(), end=" ")
    print('pid : ', os.getpid())


def drop_event(binary_files):
    file_list = []
    for file in binary_files:
        file_list.append(file.decode('gbk'))

    print(file_list)
    multiprocess_launch(file_list[0])


def open_file_event():
    file = filedialog.askopenfilename()
    print(file)
    if file:
        multiprocess_launch(file)


def open_video_folder_event():
    dir = filedialog.askdirectory()
    print(dir)
    if dir:
        multiprocess_launch(dir)


def open_image_folder_event():
    dir = filedialog.askdirectory()
    print(dir)
    if dir:
        multiprocess_launch(dir, mode="image_folder")


def open_camera_event():
    multiprocess_launch(0)


def screen_capture_event():
    multiprocess_launch("screen")


def show_help():
    tkinter.messagebox.showinfo('help', 'no help')


def show_copy_right():
    tkinter.messagebox.showinfo('copy right', 'made by zampie\nconnect me : zampielzp@gmail.com')


def run():
    window = tkinter.Tk()

    window.title("player console")
    window.geometry("400x400")
    window.iconbitmap(__file__)

    windnd.hook_dropfiles(window, func=drop_event)

    menu_bar = tkinter.Menu(window)
    file_menu = tkinter.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label='exit', command=window.quit)

    help_menu = tkinter.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label='help', command=show_help)
    help_menu.add_separator()
    help_menu.add_command(label='copy right', command=show_copy_right)

    menu_bar.add_cascade(label='file', menu=file_menu)
    menu_bar.add_cascade(label='help', menu=help_menu)
    window.config(menu=menu_bar)

    open_file_button = tkinter.Button(window, text='open file', command=open_file_event)
    open_file_button.pack()

    open_video_folder_button = tkinter.Button(window, text='open video folder', command=open_video_folder_event)
    open_video_folder_button.pack()

    open_image_folder_button = tkinter.Button(window, text='open image folder', command=open_image_folder_event)
    open_image_folder_button.pack()

    open_camera_button = tkinter.Button(window, text='open camera', command=open_camera_event)
    open_camera_button.pack()

    screen_capture_button = tkinter.Button(window, text='screen capture', command=screen_capture_event)
    screen_capture_button.pack()

    text_label = tkinter.Label(window, text="\n\n\n\n\ndraw to play")
    text_label.pack()
    window.mainloop()


if __name__ == '__main__':
    run()
