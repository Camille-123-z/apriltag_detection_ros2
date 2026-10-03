# apriltag_detection_ros2 使用教程（USB 单目摄像头）

本教程教你用 **USB 单目摄像头** 跑通 AprilTag 检测：装依赖 → 打印标签 → 标定相机 → 编译 → 运行 → 看结果 → 排错。

> 环境默认 **Ubuntu 22.04 + ROS 2 Humble**（24.04 + Jazzy 同理，把 `$ROS_DISTRO` 换掉即可）。

---

## 0. 准备清单

- [ ] Ubuntu 22.04 + ROS 2 Humble（含基础环境）
- [ ] 一个 USB 摄像头（单目，本教程按免驱 UVC 摄像头写）
- [ ] 打印好的 AprilTag **36h11** 标签（ID 0 / 1 / 2）
- [ ] 一张棋盘格标定板（用于相机标定）

---

## 1. 安装依赖

```bash
sudo apt update
sudo apt install -y \
  ros-$ROS_DISTRO-apriltag-ros \
  ros-$ROS_DISTRO-usb-cam \
  ros-$ROS_DISTRO-image-proc \
  ros-$ROS_DISTRO-camera-calibration \
  v4l-utils
```

- `apriltag-ros`：AprilTag 检测节点（本包只是它的 launch/config 封装）
- `usb-cam`：USB 相机驱动
- `image-proc`：图像矫正（去畸变）
- `camera-calibration`：相机标定工具
- `v4l-utils`：`v4l2-ctl` 命令，查看摄像头

---

## 2. 准备 AprilTag 标签

本包默认检测 **36h11 家族**的 0 / 1 / 2 号标签（见 `config/tags.yaml`）：

```yaml
tag:
  ids: [0, 1, 2]
  frames: [tag_0, tag_1, tag_2]
  sizes: [0.05, 0.04, 0.03]   # 单位：米
```

1. 下载标签图片：<https://github.com/AprilRobotics/apriltag-imgs>，进 `tag36h11/`，取 `tag36_11_00000.png`、`tag36_11_00001.png`、`tag36_11_00002.png`。
2. 打印出来（**黑色边框要完整、别缩放变形**，建议白底黑标）。
3. 用尺子量每个标签实际边长（米），改 `config/tags.yaml` 里的 `sizes`，改成你真实的尺寸。

> 尺寸越准，检测到的标签位姿（位置/朝向）越准。

---

## 3. 相机标定（USB 单目的关键一步）⭐

`config/ost.yaml` 里现在是一套**别人的相机**标定数据，你的相机直接用它，去畸变和位姿都会不准。**必须重新标定。**

### 3.1 确认你的摄像头设备号

```bash
v4l2-ctl --list-devices
```

找到你的 USB 摄像头对应的 `/dev/videoX`（通常是 `/dev/video0`，有些相机是 `/dev/video2`）。若不是 `video0`，改 `launch/camera.launch.py` 里的 `video_device`。

### 3.2 打印棋盘格

去 <https://www.optitrack.com/support/camera-calibration/> 或搜 "checkerboard pdf" 打印一张 **8×6 内角点** 的棋盘格，量出**每个小方格边长**（米），下面命令里 `--square` 填这个值。

### 3.3 启动相机（用本包的 launch）

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
ros2 launch apriltag_detection camera.launch.py
```

（先按第 4 节把包编译安装好。）

### 3.4 启动标定 GUI

另开一个终端：

```bash
ros2 run camera_calibration cameracalibrator \
  --size 8x6 --square 0.025 \
  -r image:=/usb_cam/image_raw \
  -r camera:=/usb_cam
```

> `--size` 填内角点数（宽×高，8x6），`--square` 填小方格边长（米）。

把棋盘格在镜头前**上下左右、旋转、倾斜、远近**各角度移动，直到右侧进度条 X / Y / Size / Skew 都变绿，点 **CALIBRATE**。

### 3.5 把标定结果写回 ost.yaml

标定成功后，GUI 里会显示：

- `camera matrix`（3×3 内参矩阵）
- `distortion`（畸变系数）

把这几个数抄进 `config/ost.yaml` 的 `camera_matrix.data` 和 `distortion_coefficients.data`（保持 9 个 / 5 个数字，顺序对应）。

> 也可以点 **SAVE** 存到本地，再点 **COMMIT** 写回相机（会调用 `set_camera_info` 服务）。最简单稳妥还是手动抄进 ost.yaml。

标定完，`image_proc` 发布的 `/usb_cam/image_rect` 才是正确去畸变后的图像，AprilTag 位姿才准。

---

## 4. 编译工作空间

```bash
mkdir -p ~/apriltag_ws/src
cd ~/apriltag_ws/src
# 把本仓库 clone 或复制过来，目录名必须是 apriltag_detection
git clone https://github.com/Camille-123-z/apriltag_detection_ros2.git apriltag_detection
# 或：cp -r /path/to/apriltag_detection_ros2 apriltag_detection

cd ~/apriltag_ws
colcon build --symlink-install
source install/setup.bash
```

> `--symlink-install`：改了 yaml / launch 直接生效，不用重新 build（改 `setup.py` 才需要重编）。

---

## 5. 运行

开三个终端，都先 `source ~/apriltag_ws/install/setup.bash`：

```bash
# 终端1：相机 + 矫正 + 静态TF（base_footprint -> usb_cam）
ros2 launch apriltag_detection camera.launch.py

# 终端2：AprilTag 连续检测
ros2 launch apriltag_detection continuous_detection.launch.py

# 终端3：可视化（可选）
ros2 run rviz2 rviz2 -d $(ros2 pkg prefix apriltag_detection)/share/apriltag_detection/rviz/apriltag.rviz
```

---

## 6. 查看结果

```bash
# 看有哪些话题
ros2 topic list

# 看检测结果（AprilTagDetectionArray）
ros2 topic echo /detections

# 看 TF（标签位姿）
ros2 run tf2_ros tf2_echo base_footprint tag_0
```

检测到标签后，`/detections` 里每个标签包含 id、中心像素、角点、以及**相对相机的位姿**；同时会发布 `tag_0` / `tag_1` / `tag_2` 的 TF。

带框图像话题名可能因 apriltag_ros 版本不同而异（常见 `tag_detections_image` 或 `tag_detections`），用 `ros2 topic list` 确认后再在 rviz2 里加 Image 显示。

---

## 7. USB 摄像头常见问题

| 现象 | 原因 / 解决 |
|------|------------|
| 相机打不开、`/dev/video0` 不存在 | 设备号不对。`v4l2-ctl --list-devices` 确认，改 `video_device` |
| `Could not set pixel format` | 相机不支持 `yuyv`。把 `camera.launch.py` 里 `pixel_format` 改成 `mjpeg`（或 `uyvy`）试试 |
| `Permission denied` 打不开视频设备 | 加权限：`sudo usermod -aG video $USER` 后**重新登录**，或临时 `sudo chmod 666 /dev/video0` |
| 一个相机冒出 `/dev/video0` 和 `/dev/video1` | 常见是元数据通道，用 `/dev/video0`（实际能出图的那个），`v4l2-ctl --device=/dev/video0 --list-formats-ext` 看格式 |
| 检测不到 / 位姿很飘 | ① 标签尺寸没量准 ② 没标定或标定数据是旧的 ③ 光线/反光 ④ 标签糊了（试试把 `settings.yaml` 的 `detector.decimate` 降到 0.5） |
| rviz2 里 image_rect 花屏/拉伸 | 标定没做对，先标定再看 image_rect |
| 只想先快速测试不想标定 | 把 `continuous_detection.launch.py` 里 `image_rect` 的 remap 改成 `image_raw`，直接检测原图（位姿不准，仅验证能不能检测到） |

---

## 附：话题/数据流

```
usb_cam  ──/usb_cam/image_raw──▶  image_proc  ──/usb_cam/image_rect──▶  apriltag_node
            (原始图像)              (去畸变)                                    │
                                                        /detections (AprilTagDetectionArray)
                                                        /tf  (tag_0 / tag_1 / tag_2)
```

相机标定数据 `config/ost.yaml` 被 `usb_cam` 和 `image_proc` 共同使用；检测参数在 `config/settings.yaml`，标签定义在 `config/tags.yaml`。
