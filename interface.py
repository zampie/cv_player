from src.cv_player_gui import CVPlayerGUI
import tkinter
from tkinter import filedialog

import windnd
import threading
import multiprocessing
import os


def multiprocess_launch(file, mode=None):
    play_thread = multiprocessing.Process(target=player_selector, args=(file, mode, paras))
    play_thread.start()


def player_selector(source, mode, paras):
    print('process start : ', end=" ")
    print('thread name: ', threading.currentThread().getName(), end=" ")
    print('pid : ', os.getpid())

    player = CVPlayerGUI(**paras)
    if not mode:
        player.play(source)
    elif mode == "image_folder":
        player.play_img_folder(source)

    print('process over : ', end=" ")
    print('thread name: ', threading.currentThread().getName(), end=" ")
    print('pid : ', os.getpid())


def drop_event(binary_files):
    file_list = []
    for file in binary_files:
        file_list.append(file.decode('gbk'))

    print(file_list)
    multiprocess_launch(file_list[0])
    # gui.destroy()


def open_file_event():
    file = filedialog.askopenfilename()
    print(file)
    multiprocess_launch(file)


def open_video_folder_event():
    file = filedialog.askdirectory()
    print(file)
    multiprocess_launch(file)


def open_image_folder_event():
    file = filedialog.askdirectory()
    print(file)
    multiprocess_launch(file, "image_folder")


if __name__ == '__main__':
    paras = {}

    window = tkinter.Tk()

    window.title("player console")
    window.geometry("400x400")

    windnd.hook_dropfiles(window, func=drop_event)

    open_file_button = tkinter.Button(window, text='open file', command=open_file_event)
    open_file_button.pack()

    open_video_folder_button = tkinter.Button(window, text='open video folder', command=open_video_folder_event)
    open_video_folder_button.pack()

    open_image_folder_button = tkinter.Button(window, text='open image folder', command=open_image_folder_event)
    open_image_folder_button.pack()

    text_label = tkinter.Label(window, text="\n\n\n\n\ndraw to play")
    text_label.pack()
    window.mainloop()
