import json
from IMU.imu_receiver import read_imu_data

# ===== ROS2 設定（僅在環境有 rclpy 時啟用） =====
_ros_ok = False
_ros_node = None
_ros_pub = None


def _ros_try_init():
    """懶初始化 ROS2：有 rclpy 才建立 node 與 publisher。多次呼叫也安全。"""
    global _ros_ok, _ros_node, _ros_pub
    if _ros_ok:
        return
    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import Imu

        if not rclpy.ok():
            rclpy.init()

        class _ImuNode(Node):
            def __init__(self):
                super().__init__('imu_bridge')
                self.pub = self.create_publisher(Imu, '/imu', 10)

        _ros_node = _ImuNode()
        _ros_pub = _ros_node.pub
        _ros_ok = True
    except:
        _ros_ok = False


def _ros_publish_imu(data):
    """發佈 ROS2 Imu 訊息（若 ROS 未初始化則略過）"""
    global _ros_ok, _ros_node, _ros_pub
    if not _ros_ok or _ros_pub is None:
        return
    try:
        import rclpy
        from sensor_msgs.msg import Imu

        msg = Imu()
        msg.header.stamp = _ros_node.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        msg.linear_acceleration.x = float(data['Accelerometer_X'])
        msg.linear_acceleration.y = float(data['Accelerometer_Y'])
        msg.linear_acceleration.z = float(data['Accelerometer_Z'])

        msg.angular_velocity.x = float(data['RollSpeed'])
        msg.angular_velocity.y = float(data['PitchSpeed'])
        msg.angular_velocity.z = float(data['HeadingSpeed'])

        msg.orientation.w = float(data['qw'])
        msg.orientation.x = float(data['qx'])
        msg.orientation.y = float(data['qy'])
        msg.orientation.z = float(data['qz'])

        _ros_pub.publish(msg)
        rclpy.spin_once(_ros_node, timeout_sec=0.0)
    except:
        pass


def get_imu_data():
    _ros_try_init()
    imu_data = read_imu_data()
    _ros_publish_imu(imu_data)
    return json.dumps(imu_data)
