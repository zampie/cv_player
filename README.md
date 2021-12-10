# CVPlayer
OpenCV实现的的视频播放器，支持视频，摄像头，视频文件夹，图片，图片文件夹，录屏输入。

支持帧率监视，切帧，视频录制，视频分割，图片遍历。方便地进行图片数据的批量处理，模型测试。

不同输入共享同一个图像处理流程，仅需一行代码就可以就实现目标检测等图像处理等任务的输入变更。


### 基本用法

1. 创建一个CVPlayer对象

```python
player = CVPlayer()
```

2. 选择播放源

```
# 播放视频
player.play(r"your_video_name.mp4")

# 获取摄像头
player.play(0)

# 播放视频文件夹
player.play_folder(r"your_video_folder")

# 打开图片
player.show_img(r"your_picture_name.jpg")

# 打开图片文件夹
# delay=1自动播放，delay=0等待按任意键显示下一张图片，fps：播放速度，在delay=1且帧同步开启时生效
player.show_img_folder(r"your_img_floder", delay=0, fps=1)

# 录屏
# bbox屏幕区域，bbox=None为全屏，PIL实现
player.cap_screen(bbox=None)
```



### 鼠标，键盘输入

鼠标左键： 打印当前帧ID，鼠标点击位置

鼠标右键： 截屏

空格键： 暂停，暂停后按任意键退出

x： 截屏并打开新窗口显示原图

t： 切换fps显示，fps一般为绿色

s： 保存视频的每一帧为图片，切帧时为蓝色

r： 录制视频，录制时fps为红色

注：切帧与录屏都开启时为紫色，保存路径默认为：./capture

n： 新建视频保存片段

j： 降低帧的跨度，最低为1

k： 提高帧的跨度，最高为128

esc： 退出程序




### 参数解释， 高级用法

```
player = CVPlayer(window_name="cv player",  # 窗口名
                  save_path="./capture",  # 保存路径
                  visible=True,  # 窗口是否可见，False时为静默模式，此时不接受键鼠输入
                  show_scare=0.5,  # 显示窗口的大小
                  save_img=False,  # 是否切帧
                  save_video=False,  # 是否保存视频
                  frame_stride=1,  # 帧的跨度
                  frame_id=-1,  # 启示帧id-1
                  preprocessing_fun=None,  # 前处理函数的函数指针，建议进行resize或padding等操作
                  processing_fun=None,  # 图片处理函数的函数指针，建议进行绘图操作，不支持改变图片大小
                  show_fps=True,  # 是否显示fps
                  frame_sync=False,  # 帧同步：是否限制最大帧率
                  save_suffix="_out")  # 输出切帧文件的后缀名，仅在有图片处理函数时才启用

player.preprocessing_fun = padding_to_square  # 设置图片预处理函数，此处补黑边为正方形

# 设置图片处理函数，processing_fun只接受一个img参数，封装函数或用partial填写其他参数
player.processing_fun = partial(draw_rect, rect=[400, 400, 600, 600])

# 轻松换源
# player.cap_screen()
player.play(r"your_video_name.mp4")
# player.play(0)
# player.show_img_folder(r"your_img_floder", delay=0, fps=1)
# ......
```
把画框函数替换为目标检测等图像处理函数，进行模型测试、demo演示。

注：模型载入请放在图像处理函数外部

