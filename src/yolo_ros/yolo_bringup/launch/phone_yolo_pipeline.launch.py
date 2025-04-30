# ~/ros2_ws/src/yolo_ros/yolo_bringup/launch/phone_yolo_pipeline.launch.py
# Launches: Mobile Sensor Bridge -> Image Republisher -> YOLO Node -> Detection Visualizer

import launch
import launch_ros.actions
from launch.actions import LogInfo, TimerAction, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    ld = launch.LaunchDescription()

    # --- Define Parameters for YOLO (used in constructing the command) ---
    yolo_model = 'yolov5n.pt'
    yolo_device = 'cpu'
    yolo_input_topic = '/image_raw'
    yolo_threshold = '0.2'
    yolo_use_tracking = 'False'
    yolo_use_debug = 'False'

    # --- Actions Definitions ---

    # 1. Mobile Sensor Bridge
    mobile_sensor_launch_action = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('mobile_sensor'),
            '/launch/mobile_sensors.launch.py'
        ])
    )

    # 2. Image Republisher
    republish_node_action = launch_ros.actions.Node(
        package='image_transport',
        executable='republish',
        name='image_republisher',
        arguments=['compressed', 'raw'],
        remappings=[
            ('in/compressed', '/camera/image_raw/compressed'),
            ('out', '/image_raw')
        ],
        output='screen'
    )

    # 3. Construct the YOLO launch command string using ExecuteProcess
    #    Find the yolo.launch.py file path needed for the command
    try:
        yolo_bringup_share_dir = FindPackageShare('yolo_bringup').find('yolo_bringup')
        yolo_launch_file_path = os.path.join(yolo_bringup_share_dir, 'launch', 'yolo.launch.py')
    except Exception as e:
        # Log an error if the package or file isn't found, provides better debugging
        ld.add_action(LogInfo(msg=f"Error finding yolo.launch.py: {e}. Cannot construct YOLO command."))
        # You might want to exit or handle this more gracefully depending on requirements
        yolo_launch_file_path = "ERROR_FINDING_YOLO_LAUNCH_FILE" # Placeholder

    # Build the command list IF the path was found
    if "ERROR" not in yolo_launch_file_path:
        yolo_cmd = [
            'ros2', 'launch', yolo_launch_file_path,
            f'model:={yolo_model}',
            f'device:={yolo_device}',
            f'input_image_topic:={yolo_input_topic}',
            f'threshold:={yolo_threshold}',
            f'use_tracking:={yolo_use_tracking}',
            f'use_debug:={yolo_use_debug}'
        ]
        # Create the ExecuteProcess action for YOLO
        yolo_exec_action = ExecuteProcess(
            cmd=yolo_cmd,
            output='screen'
        )
    else:
        # If yolo.launch.py wasn't found, create a dummy action or log further
        yolo_exec_action = LogInfo(msg="Skipping YOLO execution due to launch file path error.")


    # 4. Action to run the Detection Visualizer node
    visualizer_node_action = launch_ros.actions.Node(
        package='detection_visualizer',
        executable='visualizer_node',
        name='detection_visualizer',
        parameters=[{
            'input_image_topic': '/image_raw',
            'detections_topic': '/yolo/detections',
            'output_image_topic': '/yolo/annotated_image'
        }],
        output='screen'
    )


    # --- Launch Orchestration (Sequential Startup with Nested Timers) ---

    # Start the mobile sensor bridge immediately
    ld.add_action(mobile_sensor_launch_action)

    # After bridge delay, start republisher
    ld.add_action(TimerAction(
        period=3.0, # Wait 3s for bridge
        actions=[
            LogInfo(msg="Starting image republisher..."),
            republish_node_action,

            # After republisher delay, start YOLO
            TimerAction(
                period=2.0, # Wait 2s for republisher
                actions=[
                    LogInfo(msg=f"Constructed YOLO launch command: {' '.join(yolo_cmd if 'yolo_cmd' in locals() else ['YOLO CMD ERROR'])}"),
                    LogInfo(msg="Executing YOLO launch..."),
                    yolo_exec_action, # Execute the ros2 launch command for YOLO

                    # After YOLO delay, start Visualizer
                    TimerAction(
                        period=4.0, # Wait 4s for YOLO model to load etc.
                        actions=[
                            LogInfo(msg="Starting detection visualizer..."),
                            visualizer_node_action # <<< Added visualizer here
                        ]
                    )
                ]
            )
        ]
    ))

    return ld