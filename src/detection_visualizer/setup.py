from setuptools import find_packages, setup
import os # Needed for launch file installation later if added
from glob import glob # Needed for launch file installation later if added

package_name = 'detection_visualizer'

setup(
    name=package_name,
    version='0.0.0',
    # find_packages automatically finds the 'detection_visualizer' directory
    # containing __init__.py (created by ros2 pkg create) and your node script
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # If you add launch files later, uncomment and adjust this:
        # (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shadow0', # <<< CHANGE THIS
    maintainer_email='Shahazad.abdulla.engineer@gmail.com', # <<< CHANGE THIS
    description='ROS 2 node to visualize YOLO detections on an image stream.', # <<< CHANGE OR ADD DESCRIPTION
    license='Apache License 2.0', # <<< CHOOSE A LICENSE (e.g., Apache 2.0, MIT)
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # This line makes 'ros2 run detection_visualizer visualizer_node' work
            'visualizer_node = detection_visualizer.visualizer_node:main',
        ],
    },
)