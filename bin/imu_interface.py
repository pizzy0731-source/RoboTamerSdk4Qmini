# bin/imu_interface.py  --- shim
import sys
from pathlib import Path

# 加入 include/user 到搜尋路徑
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "include" / "user"))

# 匯入正式版本
from imu_interface import *
