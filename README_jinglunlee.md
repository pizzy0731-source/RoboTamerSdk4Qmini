# IdakaSdk4iduck_v1.0
![C++](https://img.shields.io/badge/Code%20Language-C++-blue.svg) 
![ONNX](https://img.shields.io/badge/Framework-ONNX-orange.svg)
![Version](https://img.shields.io/badge/Version-1.0-blue.svg)  

**This is currently Version 1.0. update at 2025/11/05**  


**Maintainer**: Jinglun Lee<br>
**Contact**: pizzy0731@gmail.com


### Features
- **qminiSdk修改成可執行版本** — 修復原廠的bug，可運行各種模式，但行走仍不穩定需調校<br>
- **履帶** — 額外加上履帶控制<br>


## Code Structure
   ```
RoboTamerSdk4Qmini/
   ├── bin/                    # The pre-trained onnx model, the config file, and the executable files
   ├── include/                # Tne header files
   ├── lib/                    # Tne dependency libraries 
   ├── source/                 # The source files
   ├── thirdparty/             # The thirdparty files
   ├── CMakeLists.txt          # Configuration file for building the executable files
   ├── README.md
   └── README_jinglunlee.md    # iDuck版本說明
   ```
### 履帶部分
* bin/joystick.py 改成 保留原本 JSON 回傳＋新增 ROS2 發佈 topic：原始搖桿資料 的版本
* bin/serial_joy_to_arduino.py：ROS2→Arduino 節點（Python）——訂閱 /joy、用差速公式把搖桿轉成左右履帶命令，並經序列埠送到 Arduino。
* 要操作履帶除了運行run_interface，還需另開一終端執行 python3 serial_joy_to_arduino.py

### Notes
* 注意serial name可能出現錯誤
* 建議將馬達(電機)與樹梅派分開供電以維持系統穩定
* 拆裝時馬達位置及連接順序務必維持一致


## Steps
### 1. 開機，將所有裝置上電


### 2. SSH到樹梅派：

#### 可以先將樹梅派接螢幕，確認IP
#### IP：動態分配，通常為192.168.0.221或192.168.0.219
#### 密碼：Qwerty~12345


### 3. 開啟終端，運行可執行檔run_interface
```bash
cd ~/RoboTamerSdk4Qmini/bin
./run_interface 
```

### 4. 調零

#### 編輯Motor_thread.hpp，將Startq改為0
#### 重新編譯一次並運行
#### 紀錄根據config.yamlaml修改Startq再編譯一次

```bash
cd ~/RoboTamerSdk4Qmini
mkdir -p build && cd build
cmake -DPLATFORM=arm64 ..
make -j
```


### 5. 運行可執行檔，按mode開啟遙控器

#### 按A進入站立模式
#### 按X進入RL模式(即可控制搖桿進行走路)
#### 按START進入準備(軟爛)模式
#### 按B退出

```bash
cd ~/RoboTamerSdk4Qmini/bin
./run_interface 
```



## Contributing

We welcome contributions from the community! Please contact us at jinglun.lee@i-daka.com before submitting pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License —— see the [LICENSE] file —— for details.

## Citation

If you use this code in your research, please cite our work:
```
@article{Chen2025GALA,
  author={Yanyun Chen, Ran Song, Jiapeng Sheng, Xing Fang, Wenhao Tan, Wei Zhang and Yibin Li},
  journal={IEEE Transactions on Automation Science and Engineering}, 
  title={A Generalist Agent Learning Architecture for Versatile Quadruped Locomotion}, 
  year={2025},
  keywords={Quadruped Robots, Versatile Locomotion, Deep Reinforcement Learning, A Single Policy Network, Multiple Critic Networks}
}

@article{Sheng2022BioInspiredRL,
  title={Bio-Inspired Rhythmic Locomotion for Quadruped Robots},
  author={Jiapeng Sheng and Yanyun Chen and Xing Fang and Wei Zhang and Ran Song and Yuan-hua Zheng and Yibin Li},
  journal={IEEE Robotics and Automation Letters},
  year={2022},
  volume={7},
  pages={6782-6789}
}

@article{Liu2024MCLER,
  author={Liu, Maoqi and Chen, Yanyun and Song, Ran and Qian, Longyue and Fang, Xing and Tan, Wenhao and Li, Yibin and Zhang, Wei},
  journal={IEEE Robotics and Automation Letters}, 
  title={MCLER: Multi-Critic Continual Learning With Experience Replay for Quadruped Gait Generation}, 
  year={2024},
  volume={9},
  number={9},
  pages={8138-8145},
  keywords={Quadrupedal robots;Task analysis;Continuing education;Optimization;Legged locomotion;Training;Motors;Continual learning;legged robots},
  doi={10.1109/LRA.2024.3418310}
}

```
