#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import time
import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

def clamp(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)

class JoyToArduino(Node):
    """
    訂閱 /joy，將軸值轉為左右履帶 (-1..1)，以 "L,R\n" 串口送給 Arduino。
    參數（可用 ros2 param set 覆蓋）：
      serial_port:   串口裝置（預設 /dev/ttyUSB0）
      baud:          鮑率（預設 115200）
      v_axis:        前進/後退軸（預設 1 = 左搖桿Y）
      w_axis:        旋轉軸（預設 2 = 右搖桿X；注意和你發 /joy 的順序一致）
      deadzone:      死區（預設 0.08）
      expo:          指數曲線（預設 0.35，0=線性；大一點手感更細膩）
      k_turn:        轉向增益（預設 0.8）
      max_scale:     輸出縮放（預設 1.0；保留門檻）
      cmd_rate_hz:   若沒新訊息也會定期重送最後指令（預設 30Hz）
      timeout_ms:    超時無 /joy 就自動煞停的毫秒數（預設 300）
    """
    def __init__(self):
        super().__init__('serial_joy_to_arduino')

        # 參數
        self.declare_parameter('serial_port', '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('v_axis', 1)
        self.declare_parameter('w_axis', 2)
        self.declare_parameter('deadzone', 0.08)
        self.declare_parameter('expo', 0.35)
        self.declare_parameter('k_turn', 0.8)
        self.declare_parameter('max_scale', 1.0)
        self.declare_parameter('cmd_rate_hz', 30.0)
        self.declare_parameter('timeout_ms', 300)

        self.port = self.get_parameter('serial_port').get_parameter_value().string_value
        self.baud = self.get_parameter('baud').get_parameter_value().integer_value
        self.v_axis = self.get_parameter('v_axis').get_parameter_value().integer_value
        self.w_axis = self.get_parameter('w_axis').get_parameter_value().integer_value
        self.deadzone = float(self.get_parameter('deadzone').value)
        self.expo = float(self.get_parameter('expo').value)
        self.k_turn = float(self.get_parameter('k_turn').value)
        self.max_scale = float(self.get_parameter('max_scale').value)
        self.cmd_rate_hz = float(self.get_parameter('cmd_rate_hz').value)
        self.timeout_ms = int(self.get_parameter('timeout_ms').value)

        # 串口
        self.ser = None
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.05)
            self.get_logger().info(f'[Serial] Opened {self.port} @ {self.baud}')
        except Exception as e:
            self.get_logger().error(f'[Serial] Open {self.port} failed: {e}')

        # 狀態
        self.last_left = 0.0
        self.last_right = 0.0
        self.last_recv_time = self.get_clock().now()

        # ROS2
        self.sub = self.create_subscription(Joy, '/joy', self.on_joy, 20)
        self.timer = self.create_timer(1.0 / self.cmd_rate_hz, self.on_timer)

    def on_joy(self, msg: Joy):
        now = self.get_clock().now()
        self.last_recv_time = now

        # 讀取軸值（缺軸則視為0）
        def get_axis(arr, idx):
            return float(arr[idx]) if 0 <= idx < len(arr) else 0.0

        raw_v = get_axis(msg.axes, self.v_axis)   # 前進/後退
        raw_w = get_axis(msg.axes, self.w_axis)   # 左右旋轉

        # 死區
        v = 0.0 if abs(raw_v) < self.deadzone else raw_v
        w = 0.0 if abs(raw_w) < self.deadzone else raw_w

        # 指數曲線（增強中小角度手感）
        v = self.apply_expo(v, self.expo)
        w = self.apply_expo(w, self.expo)

        # 差速：left = v - k*w, right = v + k*w
        left = v - self.k_turn * w
        right = v + self.k_turn * w

        # 縮放 + 限幅到 [-1, 1]
        left = clamp(left * self.max_scale, -1.0, 1.0)
        right = clamp(right * self.max_scale, -1.0, 1.0)

        self.last_left, self.last_right = left, right

    def on_timer(self):
        # 超時保護：太久沒 /joy → 發 0,0
        elapsed_ms = (self.get_clock().now() - self.last_recv_time).nanoseconds / 1e6
        if elapsed_ms > self.timeout_ms:
            self.last_left = 0.0
            self.last_right = 0.0

        # 串口輸出
        self.send_to_serial(self.last_left, self.last_right)

    def send_to_serial(self, left, right):
        if self.ser is None or not self.ser.writable():
            return
        try:
            out = f'{left:.2f},{right:.2f}\n'
            self.ser.write(out.encode())
        except Exception as e:
            # 連線斷掉時嘗試重開（不報太多錯以免洗版）
            try:
                self.ser.close()
            except:
                pass
            try:
                self.ser = serial.Serial(self.port, self.baud, timeout=0.05)
                self.get_logger().warn(f'[Serial] Reopened {self.port}')
            except Exception:
                pass

    @staticmethod
    def apply_expo(x, expo):
        """簡易 expo：y = (1-expo)*x + expo*x^3 ；expo∈[0,1]"""
        return (1.0 - expo) * x + expo * (x ** 3)

def main():
    rclpy.init()
    node = JoyToArduino()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser:
            try:
                node.ser.close()
            except:
                pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
