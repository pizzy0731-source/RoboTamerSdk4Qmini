#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import pygame

# ===== 你這把預設 mapping（可用環境變數覆蓋） =====
IDX_A      = int(os.getenv("BTN_A",      "0"))
IDX_B      = int(os.getenv("BTN_B",      "1"))
IDX_X      = int(os.getenv("BTN_X",      "2"))
IDX_Y      = int(os.getenv("BTN_Y",      "3"))
IDX_L1     = int(os.getenv("BTN_L1",     "4"))
IDX_R1     = int(os.getenv("BTN_R1",     "5"))
IDX_SELECT = int(os.getenv("BTN_SELECT", "6"))
IDX_START  = int(os.getenv("BTN_START",  "7"))
IDX_L2     = int(os.getenv("BTN_L2",     "8"))
IDX_R2     = int(os.getenv("BTN_R2",     "9"))

AX_LX = int(os.getenv("AX_LX", "0"))
AX_LY = int(os.getenv("AX_LY", "1"))
AX_RX = int(os.getenv("AX_RX", "3"))   # 你的備忘錄：右搖桿左右=3
AX_RY = int(os.getenv("AX_RY", "4"))   # 你的備忘錄：右搖桿上下=4
AX_DX = int(os.getenv("AX_DPAD_X", "6"))  # D-pad 左右在 axis 6
AX_DY = int(os.getenv("AX_DPAD_Y", "7"))  # D-pad 上下在 axis 7
DPAD_THRESH = float(os.getenv("DPAD_THRESH", "0.5"))

# ===== ROS2 設定（僅在環境有 rclpy 時啟用） =====
ROS_JOY_TOPIC = os.getenv("ROS_JOY_TOPIC", "/joy")

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
        from sensor_msgs.msg import Joy

        if not rclpy.ok():
            rclpy.init(args=None)

        class _JoyNode(Node):
            def __init__(self):
                super().__init__('qmini_joy_bridge')
                self.pub = self.create_publisher(Joy, ROS_JOY_TOPIC, 10)

        _ros_node = _JoyNode()
        _ros_pub = _ros_node.pub
        _ros_ok = True
    except Exception as e:
        # 若沒有 rclpy 或初始化失敗，保持 _ros_ok=False，主流程照常跑
        _ros_ok = False

def _ros_publish_joy(axes_list, buttons_list):
    """發佈 ROS2 Joy 訊息（若 ROS 未初始化則略過）"""
    global _ros_ok, _ros_node, _ros_pub
    if not _ros_ok or _ros_pub is None:
        return
    try:
        from sensor_msgs.msg import Joy
        from rclpy.clock import Clock
        msg = Joy()
        # 在 ROS2 中 Joy 含 header；用 node clock 取現在時間
        msg.header.stamp = _ros_node.get_clock().now().to_msg()
        msg.axes = list(map(float, axes_list))
        msg.buttons = list(map(int, buttons_list))
        _ros_pub.publish(msg)

        # 讓 rclpy 處理一次事件（非必要，但可保持時間源穩定）
        import rclpy
        rclpy.spin_once(_ros_node, timeout_sec=0.0)
    except Exception:
        pass

class JoyStick:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # 狀態變數（與舊版欄位同名）
        self.LaxiX = 0.0
        self.LaxiY = 0.0
        self.RaxiX = 0.0
        self.RaxiY = 0.0
        self.hatX  = 0
        self.hatY  = 0
        self.butA = self.butB = self.butX = self.butY = 0
        self.L1 = self.R1 = self.L2 = self.R2 = 0
        self.SELECT = self.START = 0

    # 兼容舊介面
    def initjoystick(self):
        pass

    # 安全讀取工具
    def _btn(self, idx):
        n = self.joystick.get_numbuttons()
        return self.joystick.get_button(idx) if 0 <= idx < n else 0

    def _axis(self, idx):
        n = self.joystick.get_numaxes()
        return self.joystick.get_axis(idx) if 0 <= idx < n else 0.0

    def getjoystickstates(self):
        # 讓 pygame 更新裝置狀態
        pygame.event.pump()

        # 軸
        self.LaxiX = self._axis(AX_LX)
        self.LaxiY = self._axis(AX_LY)
        self.RaxiX = self._axis(AX_RX)
        self.RaxiY = self._axis(AX_RY)

        # D-pad：若手把沒有 hat，改用 axis 6/7 合成
        if self.joystick.get_numhats() > 0:
            hx, hy = self.joystick.get_hat(0)
            self.hatX, self.hatY = int(hx), int(hy)
        else:
            dx = self._axis(AX_DX)
            dy = self._axis(AX_DY)
            self.hatX = -1 if dx < -DPAD_THRESH else (1 if dx > DPAD_THRESH else 0)
            self.hatY = -1 if dy < -DPAD_THRESH else (1 if dy > DPAD_THRESH else 0)

        # 按鍵（採用你的手把索引；不存在就回傳 0）
        self.butA = self._btn(IDX_A)
        self.butB = self._btn(IDX_B)
        self.butX = self._btn(IDX_X)
        self.butY = self._btn(IDX_Y)
        self.L1   = self._btn(IDX_L1)
        self.R1   = self._btn(IDX_R1)
        self.L2   = self._btn(IDX_L2)
        self.R2   = self._btn(IDX_R2)
        self.SELECT = self._btn(IDX_SELECT)
        self.START  = self._btn(IDX_START)

    def display(self):
        print('================')
        print('Axes:')
        print(f'LaxiX: {self.LaxiX}')
        print(f'LaxiY: {self.LaxiY}')
        print(f'RaxiX: {self.RaxiX}')
        print(f'RaxiY: {self.RaxiY}')
        print('----------------')
        print('Hat:')
        print(f'hatX: {self.hatX}')
        print(f'hatY: {self.hatY}')
        print('----------------')
        print('button:')
        print(f'butA: {self.butA}')
        print(f'butB: {self.butB}')
        print(f'butX: {self.butX}')
        print(f'butY: {self.butY}')
        print(f'L1: {self.L1}')
        print(f'R1: {self.R1}')
        print(f'L2: {self.L2}')
        print(f'R2: {self.R2}')
        print(f'SELECT: {self.SELECT}')
        print(f'START: {self.START}')
        print('================')

joy = JoyStick()

def init_joystick():
    """與舊 API 相容；同時嘗試初始化 ROS2。"""
    _ros_try_init()

def read_joystick():
    """讀取搖桿狀態；回傳 JSON（與原 SDK 相容），並同步發佈 ROS2 /joy。"""
    joy.getjoystickstates()

    # 準備 JSON（保留舊介面）
    result = {
        "LaxiX": joy.LaxiX, "LaxiY": joy.LaxiY,
        "RaxiX": joy.RaxiX, "RaxiY": joy.RaxiY,
        "hatX": joy.hatX,   "hatY": joy.hatY,
        "butA": joy.butA, "butB": joy.butB, "butX": joy.butX, "butY": joy.butY,
        "L1": joy.L1, "R1": joy.R1, "L2": joy.L2, "R2": joy.R2,
        "SELECT": joy.SELECT, "START": joy.START,
    }

    # 同步發 ROS2 Joy：把軸與按鍵映射到標準陣列
    axes_list = [joy.LaxiX, joy.LaxiY, joy.RaxiX, joy.RaxiY, float(joy.hatX), float(joy.hatY)]
    buttons_list = [
        joy.butA, joy.butB, joy.butX, joy.butY,
        joy.L1, joy.R1, joy.L2, joy.R2,
        joy.SELECT, joy.START
    ]
    _ros_publish_joy(axes_list, buttons_list)

    return json.dumps(result)


if __name__ == "__main__":
    import time
    print("[joystick] ROS2 publishing started. Press Ctrl+C to stop.")
    init_joystick()
    try:
        while True:
            read_joystick()
            time.sleep(0.05)  # 約 20Hz，可自行調整頻率
    except KeyboardInterrupt:
        print("\n[joystick] stopped.")
