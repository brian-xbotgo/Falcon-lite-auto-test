原架构：
RV1126B_Test_Tool/          # 项目根目录
├── main.py                 # 唯一程序入口：初始化APP + 启动主窗口
├── ui/                     # UI展示层（纯界面，0业务逻辑）
│   ├── __init__.py
│   ├── main_window.py      # 主窗口框架：整合所有标签页
│   ├── tab_all_test.py     # 全部测试页面UI
│   ├── tab_part_test.py    # 部分功能测试页面UI
│   ├── tab_log_view.py     # 日志查看页面UI
│   └── tab_file_manager.py # 文件管理页面UI
├── service/                # 业务服务层（核心解耦层，所有功能入口）
│   ├── __init__.py
│   ├── adb_service.py      # ADB服务：仅负责USB设备连接/命令执行
│   ├── test_service.py     # 测试服务：测试用例执行/流程控制
│   ├── log_service.py      # 日志服务：日志生成+写入data文件夹
│   └── report_service.py   # 报告服务：测试报告生成+存储
├── model/                  # 数据模型层：纯数据结构，无逻辑
│   ├── __init__.py
│   ├── device_model.py     # 设备模型：USB设备信息（序列号/状态等）
│   └── test_model.py       # 测试模型：用例/结果/报告数据结构
├── utils/                  # 工具层：全局通用工具，无业务
│   ├── __init__.py
│   ├── config.py           # 全局配置：窗口尺寸、ADB参数、数据路径等
│   └── common.py           # 公共工具：文件操作、格式转换等通用方法
└── data/                   # 数据持久层：所有输出文件统一存放
    ├── logs/               # 运行日志、操作日志
    ├── reports/            # 测试报告（Excel/TXT/HTML）
    └── firmware/           # 固件包存储（用于升级测试）


为了适配RV1126B开发板系统
data与ui文件夹不进行改动,修改并迁移service、model、utils中的内容
修改点:
整体架构重构，根据开发板的模块以及代码，再细分，将测试的用例根据功能重新分配到所属的新模块,以下是新增的文件夹及其意义:
	1. commons:全局公共工具库，包含日志、字符串处理、文件操作、时间戳、错误码定义、通用数据结构等所有模块共用的基础代码
	2. misc:杂项工具和配置，存放零散的辅助脚本、配置文件、校准参数、临时工具等不适合归类到其他模块的内容
	3. btwifi:蓝牙 + WiFi 驱动，放置相关测试用例
	4. bleConfigureWifi:蓝牙配网相关测试用例
	5. ble_central:BLE 蓝牙主机模式实现，用于设备作为中心节点连接其他 BLE 外设（如传感器、遥控器），处理 GATT 协议和数据收发，:相关测试用例
	6. http_agent: HTTP 客户端封装，用于设备向云端发送 HTTP 请求、下载文件（如 OTA 固件包）、上报设备状态等:相关测试用例
	7. mqtt_wrapper: MQTT:相关测试用例
	8. ota_update: OTA:相关测试用例
	9. sdcard_firming:SD卡:相关测试用例
	10. lvgl_app:LVGL:相关测试用例，包括两个子文件夹charge_lvgl_app（充电状态测试用例）和normal_lvgl_app（正常状态测试用例）
	11. multi_media:多媒体处理模块，音频输入输出、摄像头采集和视频流处理等:相关测试用例
	12. stepper_motor_control:步进电机控制:相关测试用例
	13. brushless_motor_control:无刷电机:相关测试用例
	14. detect:AI 检测核心模块，基于 RV1126B 的 NPU 硬件加速，实现目标检测、人脸识别、物体识别等 AI 算法的部署和推理等相关测试用例
	15. tracking：目标跟踪相关测试用例
	16. stream:流媒体传输相关测试用例

目前这是新架构的雏形，每个测试用例分配到新文件夹后还会新建子文件夹来单独放置用例，相当于每个测试用例一个文件夹(例:测试版本信息用例应该放置到misc文件夹中然后新建一个子文件夹version_info/然后放置py文件，命名也要保持规范)


