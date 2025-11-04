# bin/imu_receiver.py  --- 改成 shim 轉發 include 版本
import sys
from pathlib import Path

# 把 include/user 加進 Python 搜尋路徑
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "include" / "user"))

# 匯入正式版本
from IMU.imu_receiver import *
