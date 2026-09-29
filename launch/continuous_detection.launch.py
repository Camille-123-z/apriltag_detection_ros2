"""AprilTag 连续检测启动文件（对应 ROS 1 的 continuous_detection.launch）。

启动 apriltag_ros 的 apriltag_node，订阅 /usb_cam/image_rect 与
/usb_cam/camera_info，发布 detections（AprilTagDetectionArray）与 /tf。
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    node_namespace = LaunchConfiguration('node_namespace', default='')
    camera_name = LaunchConfiguration('camera_name', default='/usb_cam')
    image_topic = LaunchConfiguration('image_topic', default='image_rect')

    settings_file = PathJoinSubstitution([
        FindPackageShare('apriltag_detection'), 'config', 'settings.yaml'])
    tags_file = PathJoinSubstitution([
        FindPackageShare('apriltag_detection'), 'config', 'tags.yaml'])

    apriltag_node = Node(
        package='apriltag_ros',
        executable='apriltag_node',
        name='apriltag',
        namespace=node_namespace,
        parameters=[settings_file, tags_file],
        remappings=[
            # 原 ROS1: <remap from="image_rect" to="$(arg camera_name)/$(arg image_topic)" />
            ('image_rect', [camera_name, '/', image_topic]),
            ('camera_info', [camera_name, '/camera_info']),
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('node_namespace', default_value=''),
        DeclareLaunchArgument('camera_name', default_value='/usb_cam'),
        DeclareLaunchArgument('image_topic', default_value='image_rect'),
        apriltag_node,
    ])
