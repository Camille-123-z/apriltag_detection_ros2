# apriltag_detection (ROS 2)

这是 [bingda-robot/apriltag_detection](https://gitee.com/bingda-robot/apriltag_detection)（ROS 1）的 **ROS 2 移植版**。

原包是一个围绕 `apriltag_ros` 的配置/launch 封装（本身无检测代码），本 ROS 2 版保持同样的定位：启动 `apriltag_ros` 的检测节点 + `usb_cam` 相机 + `image_proc` 矫正 + 静态 TF。

## 依赖安装（ROS 2）

```bash
sudo apt install ros-$ROS_DISTRO-apriltag-ros \
                ros-$ROS_DISTRO-usb-cam \
                ros-$ROS_DISTRO-image-proc
```

> `$ROS_DISTRO` 换成你的发行版，如 `humble` / `jazzy`。

## 编译

把本目录放进你的 ROS 2 工作空间 `src/` 下，例如：

```bash
mkdir -p ~/apriltag_ws/src
cp -r apriltag_detection_ros2 ~/apriltag_ws/src/apriltag_detection
cd ~/apriltag_ws
colcon build --symlink-install
source install/setup.bash
```

## 运行

```bash
# 终端1：启动相机 + 矫正 + 静态TF
ros2 launch apriltag_detection camera.launch.py

# 终端2：AprilTag 连续检测
ros2 launch apriltag_detection continuous_detection.launch.py

# 可视化（rviz2 里 Fixed Frame 设 base_footprint，添加 TF / Image）
ros2 run rviz2 rviz2 -d $(ros2 pkg prefix apriltag_detection)/share/apriltag_detection/rviz/apriltag.rviz
```

检测结果话题：`/detections`（`apriltag_msgs/msg/AprilTagDetectionArray`），并发布标签 TF（`tag_0` / `tag_1` / `tag_2`）。

## ROS1 → ROS2 改动对照

| 项 | ROS 1（原包） | ROS 2（本包） |
|----|--------------|--------------|
| 检测节点 | `apriltag_ros` 的 `apriltag_ros_continuous_node` | `apriltag_ros` 的 `apriltag_node` |
| 相机节点 | `usb_cam` 的 `usb_cam_node` | `usb_cam` 的 `usb_cam_node_exe` |
| 图像矫正 | `image_proc` 的 `image_proc` | `image_proc` 的 `image_proc`（executable 同名） |
| 静态 TF | `tf` 的 `static_transform_publisher` | `tf2_ros` 的 `static_transform_publisher`（参数用 `--x/--roll/...`） |
| 标签家族 | `tag_family: tag36h11` | `family: 36h11`（去掉 `tag` 前缀） |
| 标签定义 | `standalone_tags: [{id, size}, ...]` | `tag.ids` / `tag.frames` / `tag.sizes` 三个等长列表 |
| 检测线程 | `tag_threads: 2` | `detector.threads: 2` |
| 图像传输 | `transport_hint: "raw"` | `image_transport: raw` |
| 参数文件 | `<rosparam command="load" ...>` | YAML 用 `/**:` + `ros__parameters:`，launch 里 `parameters=[...]` 加载 |

## 注意事项

- **相机标定**：`config/ost.yaml` 是 camera_info_manager 格式（ROS1/ROS2 通用），按你的相机重新标定后替换。
- **标签尺寸**：`config/tags.yaml` 里 `sizes` 的单位是米，按实际打印尺寸改。
- **检测图像话题**：ROS 2 的 `apriltag_ros` 发布带框图像的 topic 可能与 ROS1 的 `/tag_detections_image` 不同，用 `ros2 topic list` 确认后再在 rviz2 里选。
- **rviz 配置**：`rviz/apriltag.rviz` 是尽力移植的最小配置，若 rviz2 提示无法加载某些显示，手动重新添加 TF / Image 即可。
