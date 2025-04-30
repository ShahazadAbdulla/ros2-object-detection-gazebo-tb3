#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo # CameraInfo maybe needed later
from yolo_msgs.msg import DetectionArray, Detection, BoundingBox2D
import cv2
from cv_bridge import CvBridge

class VisualizerNode(Node):

    def __init__(self):
        super().__init__('detection_visualizer_node')

        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('detections_topic', '/yolo/detections')
        self.declare_parameter('output_image_topic', '/yolo/annotated_image')

        input_image_topic = self.get_parameter('input_image_topic').get_parameter_value().string_value
        detections_topic = self.get_parameter('detections_topic').get_parameter_value().string_value
        output_image_topic = self.get_parameter('output_image_topic').get_parameter_value().string_value

        self.bridge = CvBridge()
        self.latest_cv_image = None
        self.latest_detections = []
        self.latest_header = None # <-- Added to store header
        self.image_received_flag = False

        self.image_subscriber = self.create_subscription(
            Image, input_image_topic, self.image_callback, 10)
        self.detection_subscriber = self.create_subscription(
            DetectionArray, detections_topic, self.detections_callback, 10)
        self.annotated_image_publisher = self.create_publisher(
            Image, output_image_topic, 10)
        self.processing_timer = self.create_timer(0.05, self.timer_callback) # ~20 Hz

        self.get_logger().info(f"Detection Visualizer Node Started!")
        self.get_logger().info(f"Input Image Topic: {input_image_topic}")
        self.get_logger().info(f"Detections Topic: {detections_topic}")
        self.get_logger().info(f"Output Annotated Topic: {output_image_topic}")

    def image_callback(self, msg: Image):
        # self.get_logger().debug('Received image')
        try:
            self.latest_cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.latest_header = msg.header # <-- Store header from this message
            self.image_received_flag = True
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")

    def detections_callback(self, msg: DetectionArray):
        # self.get_logger().debug(f'Received {len(msg.detections)} detections')
        self.latest_detections = msg.detections # Store the list of Detection objects

    def timer_callback(self):
        # Check if we have data needed to process
        if not self.image_received_flag or self.latest_cv_image is None or self.latest_header is None:
            # self.get_logger().warn("Timer callback: Waiting for image and header.")
            return

        # Make copies to work on
        annotated_image = self.latest_cv_image.copy()
        current_detections = list(self.latest_detections) # Shallow copy is ok for the list itself

        # Draw detections if any exist
        if current_detections:
            # Define drawing parameters
            box_color = (0, 255, 0)  # Green (BGR)
            box_thickness = 2
            text_color = (0, 255, 0)
            text_font = cv2.FONT_HERSHEY_SIMPLEX
            text_scale = 0.6
            text_thickness = 1

            for det in current_detections: # type: Detection
                try:
                    # Extract bounding box info (handle potential non-existence)
                    if det.bbox: # Check if bbox exists
                        center_x = int(det.bbox.center.position.x)
                        center_y = int(det.bbox.center.position.y)
                        size_x = int(det.bbox.size.x)
                        size_y = int(det.bbox.size.y)

                        # Calculate corners
                        x1 = max(0, center_x - size_x // 2) # Add max(0,...) to prevent negative coords
                        y1 = max(0, center_y - size_y // 2)
                        x2 = center_x + size_x // 2
                        y2 = center_y + size_y // 2

                        # Draw rectangle
                        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), box_color, box_thickness)

                        # Prepare label
                        score_percent = f"{det.score * 100:.1f}%"
                        label = f"{det.class_name} {score_percent}"

                        # Put text
                        cv2.putText(annotated_image, label, (x1, y1 - 5),
                                    text_font, text_scale, text_color, text_thickness)
                except Exception as e:
                    self.get_logger().error(f"Error drawing detection: {det} - {e}")
        # else: If no detections, annotated_image remains a copy of latest_cv_image

        # Publish the result
        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
            annotated_msg.header = self.latest_header # Assign the stored header
            self.annotated_image_publisher.publish(annotated_msg)
        except Exception as e:
            self.get_logger().error(f"Failed to publish annotated image: {e}")

# --- Main function remains the same ---
def main(args=None):
    rclpy.init(args=args)
    visualizer_node = VisualizerNode()
    try:
        rclpy.spin(visualizer_node)
    except KeyboardInterrupt:
        visualizer_node.get_logger().info('Node stopped cleanly by user')
    finally:
        visualizer_node.destroy_node()
        rclpy.shutdown()
        visualizer_node.get_logger().info('ROS resources shut down')

if __name__ == '__main__':
    main()