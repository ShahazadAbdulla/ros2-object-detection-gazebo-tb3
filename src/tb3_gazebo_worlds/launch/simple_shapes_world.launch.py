# ~/ros2_ws/src/tb3_gazebo_worlds/launch/simple_shapes_world.launch.py
# FINAL (?) Version: Adapting official TB3 RSP and Spawner methods

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # --- Get Environment Variable (Critical for Official Logic) ---
    # Read from env var, default to waffle if not set
    # Make sure this is exported in the terminal running the launch file!
    turtlebot3_model_env = os.environ.get('TURTLEBOT3_MODEL', 'waffle')
    if 'TURTLEBOT3_MODEL' not in os.environ:
        print("TURTLEBOT3_MODEL environment variable not set, defaulting to 'waffle'")


    # --- Launch Arguments ---
    # Argument for our custom world file
    declare_world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(
            get_package_share_directory('tb3_gazebo_worlds'),
            'worlds', 'simple_shapes.world'),
        description='Full path to world file to load')

    # Argument for use_sim_time (used by multiple nodes)
    declare_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    # Arguments for start pose (passed to spawner)
    declare_x_arg = DeclareLaunchArgument('x_pose', default_value='0.0')
    declare_y_arg = DeclareLaunchArgument('y_pose', default_value='0.0')
    declare_yaw_arg = DeclareLaunchArgument('yaw', default_value='0.0')


    # Get LaunchConfiguration objects
    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    yaw = LaunchConfiguration('yaw')


    # --- Get Package Paths ---
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_tb3_description = get_package_share_directory('turtlebot3_description')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')


    # --- Node / Action Definitions ---

    # 1. Start Gazebo Server with OUR custom world
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world, 'pause': 'false'}.items()
    )

    # 2. Start Gazebo Client
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    # 3. Robot State Publisher (Logic copied from official rsp.py)
    #    Reads URDF content based on ENV VAR and passes as parameter
    urdf_file_name = f'turtlebot3_{turtlebot3_model_env}.urdf'
    urdf_path = os.path.join(pkg_tb3_description, 'urdf', urdf_file_name)
    robot_description_content = ""
    try:
        with open(urdf_path, 'r') as infp:
            robot_description_content = infp.read()
    except FileNotFoundError:
         print(f"ERROR: Could not read URDF file at {urdf_path}. Check TURTLEBOT3_MODEL env var ('{turtlebot3_model_env}')?")

    robot_state_publisher_cmd = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description_content
            }]
    )

    # 4. Spawn TurtleBot3 Model (Logic adapted from official spawn.py)
    #    Uses ENV VAR for model name and spawns the SDF file.
    model_folder = f'turtlebot3_{turtlebot3_model_env}'
    sdf_path = os.path.join(pkg_tb3_gazebo, 'models', model_folder, 'model.sdf')
    if not os.path.exists(sdf_path):
        print(f"ERROR: SDF file not found at {sdf_path}. Check TURTLEBOT3_MODEL env var ('{turtlebot3_model_env}')?")
        # Handle error appropriately - maybe don't add spawn command if file missing

    spawn_turtlebot3_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='entity_spawner',
        output='screen',
        arguments=[
            '-entity', turtlebot3_model_env, # Entity name from ENV VAR
            '-file', sdf_path,             # Use SDF FILE path
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.01',                  # Default Z from original spawn file
            '-Y', yaw
        ]
    )

    # --- Create Launch Description ---
    ld = LaunchDescription()

    # Declare arguments
    ld.add_action(declare_world_arg)
    ld.add_action(declare_sim_time_arg)
    ld.add_action(declare_x_arg)
    ld.add_action(declare_y_arg)
    ld.add_action(declare_yaw_arg)
    # We don't strictly need to declare 'model' anymore as it's read from ENV,
    # but keeping it allows potential overrides if launch arguments could somehow
    # set env vars for child processes (complex).

    # Start Gazebo
    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)

    # Start Robot State Publisher (publishes TF based on URDF)
    ld.add_action(robot_state_publisher_cmd)

    # Wait, then spawn robot (using SDF)
    ld.add_action(TimerAction(
        period=5.0, # Wait 5s for Gazebo server and RSP to be ready
        actions=[
            LogInfo(msg='Spawning TurtleBot3 model using SDF...'),
            spawn_turtlebot3_cmd
        ]
    ))

    return ld