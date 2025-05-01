# ROS 2 Gazebo Object Detection with TurtleBot3 and YOLO

This ROS 2 workspace contains Project of a guided learning journey, demonstrating object detection within the Gazebo simulator using a TurtleBot3 Waffle model, its simulated camera, and the YOLOv5/v8 object detection framework.

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/1caa4e0c-a469-4670-a01e-adf03fc5bdbc" alt="Description for Image 1" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/f4d44fbb-de6d-412e-82ab-1eb8e2238f30" alt="Description for Image 2" width="400"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/57261b9c-4379-4101-b031-811989dbe09e" alt="Description for Image 3" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/5bf9e977-d7a2-40e9-98d5-bd16b1f31a3d" alt="Description for Image 4" width="400"/></td>
  </tr>
</table>

## Current Status (as of 01-05-2025) - Project Completed

*   **Gazebo Simulation:** Successfully launched the Gazebo simulator with a custom world containing primitive shapes (box, sphere, cylinder) and a TurtleBot3 Waffle robot model. Utilizes standard `gazebo_ros` launch components and a custom package (`tb3_gazebo_worlds`) for the world file and simulation launch.
*   **Simulated Camera:** The TurtleBot3 Waffle's simulated camera correctly publishes `sensor_msgs/msg/Image` data on the `/camera/image_raw` topic.
*   **YOLO Integration:** Integration of the [`yolo_ros`](https://github.com/mgonzs13/yolo_ros) package running YOLOv5n on CPU (`device:=cpu`, `model:=yolov5n.pt`).
*   **Successful Detection:** The core `/yolo/yolo_node` successfully subscribes to the simulated camera's `/image_raw` topic and publishes `yolo_msgs/msg/DetectionArray` on `/yolo/detections` when viewing the primitive shapes (though classifications may be inaccurate for simple geometry).
*   **Custom Visualization:** The custom Python node (`detection_visualizer/visualizer_node.py`) successfully subscribes to `/image_raw` and `/yolo/detections`, draws bounding boxes/labels using OpenCV, and publishes the annotated result on `/yolo/annotated_image`.
*   **Teleoperation:** Robot can be controlled within the Gazebo world using `turtlebot3_teleop` package to test camera views and detections.
*   **Launch Files:** Uses separate launch files: one in `tb3_gazebo_worlds` to start the simulation and robot, and another in `yolo_bringup` (or potentially a new master launch file) to start the perception pipeline (YOLO + Visualizer).

## Packages Used / Structure

This workspace (`ros2_ws`) utilizes the following key packages located in `src/`:

1.  **`yolo_ros` (Git Repo containing multiple packages):** Clone of [`yolo_ros`](https://github.com/mgonzs13/yolo_ros). Builds `yolo_msgs`, `yolo_ros`, `yolo_bringup`. Provides YOLO integration nodes and launch files.
2.  **`detection_visualizer`:** Custom package containing the Python node (`visualizer_node.py`) for drawing detection bounding boxes.
3.  **`tb3_gazebo_worlds`:** Custom package containing:
    *   `worlds/primitives_world.world`: A simple Gazebo world file with ground, sun, and basic shapes defined via SDF.
    *   `launch/simple_shapes_world.launch.py`: Launch file to start Gazebo with the custom world and spawn a TurtleBot3 Waffle.

*(The `mobile_sensor` package is not required for this Gazebo-based project phase).*

## Key Concepts Demonstrated / Learned (Building on Previous)

*   **Gazebo Simulation:** Launching Gazebo with ROS 2, understanding Worlds vs Models.
*   **SDF/URDF:** Using existing descriptions (`turtlebot3_description`, `turtlebot3_gazebo`) and creating a basic `.world` file with primitive shapes and standard plugins (Ground, Sun, Physics, ROS Integration). Understood the concept of Gazebo ROS Plugins.
*   **Simulated Sensors:** Interfacing with a simulated camera publishing standard ROS `Image` messages.
*   **Robot Spawning:** Using `gazebo_ros/spawn_entity.py` with SDF files.
*   **Robot State Publisher:** Understanding its role in publishing TF from joint states based on URDF.
*   **TF (Transforms):** Observing TF frames published by `robot_state_publisher` and Gazebo (relevant for interpreting 3D data, although not heavily used in this 2D detection viz).
*   **Environment Variables:** Setting and using `TURTLEBOT3_MODEL` for simulation configuration. Understanding the role (and potential issues with) `GAZEBO_MODEL_PATH`.
*   **Reinforced:** Node communication, launch files, parameters, messages, debugging techniques (`rqt_graph`, etc.) in a simulation context.

## Prerequisites

*   ROS 2 Humble Hawksbill installed (**Desktop Install** recommended, includes Gazebo, Rviz, Nav2 basics).
*   Git.
*   Standard ROS 2 build tools (`colcon-common-extensions`, `rosdep`). Ensure `rosdep` is initialized (`sudo rosdep init`, `rosdep update`).
*   Required TurtleBot3 Packages:
    ```bash
    sudo apt update
    sudo apt install ros-humble-turtlebot3 ros-humble-turtlebot3-msgs ros-humble-turtlebot3-simulations ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-teleop
    ```
*   Required Gazebo Packages (should be included with Desktop or `simulations`, but good to verify):
    ```bash
    sudo apt install ros-humble-gazebo-ros-pkgs
    ```
*   Required Perception/Visualization Tools:
    ```bash
    sudo apt install ros-humble-rqt-image-view ros-humble-image-transport-plugins ros-humble-rqt-graph python3-opencv
    ```
*   Python 3 / Pip (compatible with Humble).

## Setup Instructions

1.  **Clone this Workspace Repository:**
    *(Replace URL with your actual GitHub repo URL)*
    ```bash
    git clone https://github.com/ShahazadAbdulla/ros2-object-detection-gazebo-tb3.git ~/ros2_ws # Or your desired location
    cd ~/ros2_ws
    ```
    *(This assumes the repo contains `src/yolo_ros`, `src/detection_visualizer`, and `src/tb3_gazebo_worlds`).*

2.  **Install Python Dependencies:**
    ```bash
    pip install -r src/yolo_ros/requirements.txt
    pip install opencv-python # If not installed via rosdep/apt
    ```

3.  **Initialize and Install ROS Dependencies:**
    ```bash
    # Run only if you haven't run rosdep init before
    # sudo rosdep init
    rosdep update
    rosdep install --from-paths src --ignore-src -r -y
    ```

4.  **Build the Workspace:**
    ```bash
    colcon build --symlink-install
    ```

5.  **Configure Environment Variable:** Set the TurtleBot3 model. Add this line to your `~/.bashrc` file:
    ```bash
    export TURTLEBOT3_MODEL=waffle
    ```
    Apply by running `source ~/.bashrc` in *all* terminals used for this project or by opening new ones after editing. Verify with `echo $TURTLEBOT3_MODEL`.

## How to Run the Gazebo Simulation and Detection

1.  **Source Workspace:** Open *every new terminal* and run:
    ```bash
    cd ~/ros2_ws
    source install/setup.bash
    ```
    *(Make sure the `TURTLEBOT3_MODEL` environment variable is correctly set to `waffle` in each terminal due to sourcing `.bashrc` or exporting manually)*.

2.  **Terminal 1: Launch Gazebo Simulation:**
    ```bash
    # Launches Gazebo with the custom primitive world and spawns the Waffle bot
    ros2 launch tb3_gazebo_worlds simple_shapes_world.launch.py
    ```
    *(Wait for Gazebo to load fully and the robot to appear stably)*

3.  **Terminal 2: Launch YOLO Node:**
    ```bash
    # Find the camera topic first (if unsure): ros2 topic list | grep image_raw
    # Assuming it's /camera/image_raw:
    ros2 launch yolo_bringup yolo.launch.py \
        model:=yolov5n.pt \
        device:=cpu \
        input_image_topic:=/camera/image_raw \
        threshold:=0.25 \
        use_tracking:=False \
        use_debug:=False
    ```

4.  **Terminal 3: Launch Visualizer Node:**
    ```bash
    # Ensure the input_image_topic matches the camera output topic
    ros2 run detection_visualizer visualizer_node --ros-args \
        -p input_image_topic:=/camera/image_raw \
        -p detections_topic:=/yolo/detections \
        -p output_image_topic:=/yolo/annotated_image
    ```

5.  **Terminal 4 (Optional): Teleop the Robot:**
    ```bash
    ros2 run turtlebot3_teleop teleop_keyboard
    ```

6.  **Terminal 5: View Annotated Output:**
    ```bash
    rqt_image_view /yolo/annotated_image
    ```
    *   Drive the robot in Gazebo so its camera points at the primitive shapes (box, sphere, cylinder). Bounding boxes (possibly with misclassifications) should appear in the `rqt_image_view` window.

## Credits & Acknowledgements

*   **`yolo_ros` Package:** Created by **`mgonzs13`**. ([GitHub Repo](https://github.com/mgonzs13/yolo_ros))
*   **TurtleBot3 Packages:** ROBOTIS and Open Robotics maintainers.
*   **Gazebo & Gazebo ROS Packages:** Open Robotics maintainers.
*   **YOLO Models & Ultralytics:** Based on the work by Ultralytics and the original YOLO authors. ([Ultralytics](https://ultralytics.com/))
*   **ROS 2 Tutorials & Community:** Leveraging concepts and tools from the broader ROS 2 ecosystem and documentation.

## Next Steps / Future Work (Welcome to try)

*   **(Self-Study/Exploration):** Learn more detailed SDF/URDF syntax for creating custom robots and worlds.
*   **Performance Tuning:** Experiment with different YOLO model sizes (e.g., YOLOv8n).
*   **Explore GPU Acceleration (Optional):** Investigate CUDA setup and run YOLO with `device:=cuda:0`.
*   **Rviz Visualization:** Create an Rviz configuration (`.rviz` file) to visualize the robot model, TF frames, LiDAR scan (`/scan`), camera feed, and potentially detection markers (`/yolo/dgb_bb_markers` if that topic works and publishes valid markers).
*   **Next Project (e.g., Path Planning):** Move on to Project 4, likely using Gazebo, TurtleBot3, Nav2 stack, and Rviz.
*   **C++ Implementation:** Reimplement parts of this perception pipeline (e.g., the visualizer node) in C++ for practice.
