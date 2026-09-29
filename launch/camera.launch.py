"""相机启动文件（对应 ROS 1 的 camera.launch）。

启动 usb_cam（相机驱动）+ image_proc（图像矫正）+ 静态 TF（base_footprint -> usb_cam）。
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # USB 相机驱动（ROS 2 可执行文件名为 usb_cam_node_exe，非 ROS1 的 usb_cam_node）
    usb_cam = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        parameters=[{
            'video_device': '/dev/video0',
            'image_width': 640,
            'image_height': 480,
            'pixel_format': 'yuyv',
            'camera_frame_id': 'usb_cam',
            'io_method': 'mmap',
            'camera_name': 'usb_cam',
            # camera_info_manager 支持 package:// 路径
            'camera_info_url': 'package://apriltag_detection/config/ost.yaml',
        }],
        output='screen',
    )

    # 图像矫正，发布 image_rect 等（等价 ROS1 的 image_proc nodelet）
    image_proc = Node(
        package='image_proc',
        executable='image_proc',
        name='image_proc',
        namespace='usb_cam',
        output='screen',
    )

    # 静态 TF：base_footprint -> usb_cam
    # 原 ROS1 参数: -0.04 0.0 0.05 -1.57 0.0 -1.57 base_footprint usb_cam 20
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_camera',
        arguments=[
            '--x', '-0.04', '--y', '0.0', '--z', '0.05',
            '--roll', '-1.57', '--pitch', '0.0', '--yaw', '-1.57',
            '--frame-id', 'base_footprint', '--child-frame-id', 'usb_cam',
        ],
    )

    return LaunchDescription([usb_cam, image_proc, static_tf])
