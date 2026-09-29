import os
from glob import glob
from setuptools import setup

package_name = 'apriltag_detection'

setup(
    name=package_name,
    version='0.0.0',
    # 纯配置/launch 包，无 Python 模块
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'),
         glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bingda',
    maintainer_email='bingda@todo.todo',
    description='ROS 2 launch/config wrapper for AprilTag detection (apriltag_ros)',
    license='MIT',
)
