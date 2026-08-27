import time
import requests
import json
from datetime import datetime

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
    from std_msgs.msg import Header
    from sensor_msgs.msg import NavSatFix
    from rover_interfaces.msg import SoilTelemetry
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False

from backend.app.services.state_machine import RoverStateMachine

class RoverSimulatorNode:
    """
    ROS 2 Telemetry Publisher & 4-State Rover State Machine Node.
    Publishes to `/rover/soil_telemetry` with Reliable QoS.
    Provides standalone fallback mode when ROS 2 is not sourced.
    """

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.state_machine = RoverStateMachine()
        
        if ROS2_AVAILABLE:
            rclpy.init()
            self.node = Node("rover_simulator_node")
            qos = QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE,
                history=HistoryPolicy.KEEP_LAST,
                depth=10
            )
            self.publisher = self.node.create_publisher(SoilTelemetry, "/rover/soil_telemetry", qos)
            self.node.get_logger().info("ROS 2 Soil Telemetry Publisher Node Active on /rover/soil_telemetry")
        else:
            print("ROS 2 Python bindings not detected in current shell. Running in HTTP REST Fallback Publisher mode.")

    def run_step(self):
        status = self.state_machine.step()
        
        # If new telemetry available during INTERROGATION -> RETRACTION transition
        if status.get("latest_telemetry"):
            telemetry = status["latest_telemetry"]
            
            # 1. Publish to ROS 2 topic if available
            if ROS2_AVAILABLE:
                msg = SoilTelemetry()
                msg.header.stamp = self.node.get_clock().now().to_msg()
                msg.header.frame_id = "rover_base_link"
                
                msg.location.latitude = float(telemetry["latitude"])
                msg.location.longitude = float(telemetry["longitude"])
                msg.location.altitude = float(telemetry.get("altitude", 0.0))
                
                msg.ph = float(telemetry["ph"])
                msg.ec = float(telemetry["ec"])
                msg.moisture = float(telemetry["moisture"])
                
                msg.nitrogen = int(telemetry["nitrogen"])
                msg.phosphorus = int(telemetry["phosphorus"])
                msg.potassium = int(telemetry["potassium"])
                
                msg.rover_state = str(telemetry["rover_state"])
                msg.mission_id = str(telemetry["mission_id"])
                msg.sample_id = str(telemetry["sample_id"])
                
                self.publisher.publish(msg)
                self.node.get_logger().info(f"Published ROS 2 telemetry for Sample {msg.sample_id}")

            # 2. Forward to FastAPI backend HTTP REST Endpoint
            try:
                resp = requests.post(f"{self.api_url}/api/telemetry", json=telemetry, timeout=2.0)
                if resp.status_code == 201:
                    print(f"Successfully transmitted telemetry {telemetry['sample_id']} to FastAPI backend.")
            except Exception as e:
                print(f"HTTP REST transmission failed: {e}")

def main():
    sim = RoverSimulatorNode()
    print("Starting Autonomous Rover Simulation Loop...")
    try:
        while True:
            sim.run_step()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Simulation terminated cleanly.")

if __name__ == "__main__":
    main()
