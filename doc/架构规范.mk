好！我们**完全不涉及代码**，只做**最终版项目架构定型**，严格匹配你的需求：
✅ 基于你现有目录优化
✅ 主打 **USB有线ADB连接**
✅ **日志/测试报告** 统一归档到 `data/`
✅ 彻底解耦、分层清晰、无冗余、无交叉修改
✅ 模块化测试用例分离，按功能模块独立管理
✅ ✅ 已完成旧架构迁移，service/model/utils已废弃
✅ ✅ 引擎已整合到commons，微内核架构完成

---

# 一、最终定型：项目标准目录架构（清理冗余+明确用途）
**已删除旧的 `service/`、`model/`、`utils/`、根目录engine目录**，所有内容已迁移至新架构，最终结构如下：
```
RV1126B_Test_Tool/          # 项目根目录
├── main.py                 # 唯一程序入口：初始化APP + 启动主窗口
├── ui/                     # UI展示层（纯界面，0业务逻辑）
│   ├── __init__.py
│   ├── main_window.py      # 主窗口框架：整合所有标签页
│   ├── tab_all_test.py     # 全部测试页面UI
│   ├── tab_part_test.py    # 部分功能测试页面UI
│   ├── tab_log_view.py     # 日志查看页面UI
│   └── tab_file_manager.py # 文件管理页面UI
├── commons/                # ✅ 全局公共核心（所有基础能力整合）
│   ├── __init__.py
│   ├── log_service.py      # 日志服务：日志生成+写入data文件夹
│   ├── adb_service.py      # ADB服务：仅负责USB设备连接/命令执行
│   ├── device_model.py     # 设备模型：USB设备信息（序列号/状态等）
│   ├── test_model.py       # 测试模型：用例/结果/报告数据结构
│   ├── config.py           # 全局配置：窗口尺寸、ADB参数、数据路径等
│   ├── common.py           # 公共工具：文件操作、格式转换等通用方法
│   └── engine/             # ✅ 测试引擎核心（微内核，稳定不变）
│       ├── __init__.py
│       ├── test_service.py # 测试调度引擎：测试用例执行/流程控制
│       └── report_service.py # 报告生成引擎：测试报告生成+存储
├── misc/                   # ✅ 杂项工具和配置
│   ├── __init__.py
│   └── version_info/       # 版本信息测试用例
│       ├── __init__.py
│       └── test_version_read.py
├── btwifi/                 # ✅ 蓝牙 + WiFi 驱动
│   ├── __init__.py
│   └── network_test/       # 网络测试用例
│       ├── __init__.py
│       └── test_network_connectivity.py
├── bleConfigureWifi/       # ✅ 蓝牙配网相关测试用例
│   └── __init__.py
├── ble_central/            # ✅ BLE 蓝牙主机模式
│   └── __init__.py
├── http_agent/             # ✅ HTTP 客户端封装
│   └── __init__.py
├── mqtt_wrapper/           # ✅ MQTT 封装
│   └── __init__.py
├── ota_update/             # ✅ OTA 升级
│   └── __init__.py
├── sdcard_firming/         # ✅ SD卡
│   └── __init__.py
├── lvgl_app/               # ✅ LVGL 界面
│   ├── __init__.py
│   ├── charge_lvgl_app/    # 充电状态测试用例
│   │   └── __init__.py
│   └── normal_lvgl_app/    # 正常状态测试用例
│       └── __init__.py
├── multi_media/            # ✅ 多媒体处理
│   └── __init__.py
├── stepper_motor_control/  # ✅ 步进电机控制
│   └── __init__.py
├── brushless_motor_control/# ✅ 无刷电机
│   └── __init__.py
├── detect/                 # ✅ AI 检测核心模块
│   └── __init__.py
├── tracking/               # ✅ 目标跟踪
│   └── __init__.py
├── stream/                 # ✅ 流媒体传输
│   └── __init__.py
└── data/                   # 数据持久层：所有输出文件统一存放（核心需求）
    ├── logs/               # 运行日志、操作日志
    ├── reports/            # 测试报告（Excel/TXT/HTML）
    └── firmware/           # 固件包存储（可选，用于升级测试）
```

---

# 二、分层职责与解耦规则（核心！保证不改多文件）
我们采用 **插件化微内核架构**，内核100%稳定，功能模块完全可插拔：

## 1. 依赖方向（绝对禁止反向/跨层调用）
```
UI层 → commons.engine → 功能模块层 → commons基础层 → 系统库
```
- UI只调用commons导出的公共接口
- engine内核只负责调度，不包含任何业务逻辑
- 功能模块（测试用例）只依赖commons公共接口
- commons基础层完全独立，不依赖任何上层

## 2. 每层绝对边界（各司其职，绝不越界）
| 层级         | 核心职责 | 禁止操作 |
|--------------|----------|----------|
| **UI层**     | 仅做界面渲染、按钮点击、数据展示 | 不写任何ADB/测试/文件逻辑 |
| **commons.engine** | 测试调度、报告生成等纯调度逻辑 | 不实现任何具体测试用例、不操作UI |
| **功能模块层**| 各功能独立测试用例实现 | 不操作UI、不处理全局调度 |
| **commons基础层** | 全局公共基础能力（日志、ADB、配置、工具、数据模型） | 不绑定业务、不处理具体测试逻辑 |
| **data目录** | 唯一数据出口（日志+报告全存在这） | 不存放代码/配置 |

---

# 三、✅ 插件化测试机制（新增用例零修改核心）
## 新增测试用例只需要3步，**完全不需要修改任何核心代码**：
```
1. 在对应功能模块下新建文件夹（如：misc/new_feature/）
2. 创建test_xxx.py文件，实现测试函数
3. 给测试函数加上 @register_test_case("A003") 装饰器
```

## ✅ 测试用例编号规范
| 前缀 | 类型 | 执行顺序 |
|------|------|----------|
| `A` | 自动化测试用例 | 优先执行，所有A类用例按编号顺序执行 |
| `B` | 人工测试用例 | 所有A类完成后执行，按编号顺序执行 |

- 编号格式：`Axxx` 或 `Bxxx`，xxx为3位数字自增
- 执行顺序自动保证：先A后B，同类按编号排序
- 无需手动排序，引擎自动处理

- 引擎启动时自动扫描所有功能模块
- 自动注册所有带装饰器的测试用例
- 核心代码零修改，完全解耦

---

# 四、模块功能对应表（一目了然）
| 模块文件                  | 对应功能（完全匹配你的UI页面） |
|---------------------------|--------------------------------|
| tab_all_test.py           | 调用 `commons.TestService` + `commons.ADBService`，右侧显示测试用例实时状态 |
| tab_part_test.py          | 调用 `commons.TestService`（单测用例） |
| tab_log_view.py           | 读取 `data/logs/` 日志文件 |
| tab_file_manager.py       | 管理 `data/` 下的报告/固件 |
| commons/adb_service.py    | USB设备扫描、命令执行 |
| commons/log_service.py    | 写日志到 `data/logs/` |
| commons/engine/report_service.py | 生成报告到 `data/reports/` |
| commons/engine/test_service.py | 测试用例调度、自动发现注册 |
| **功能模块/**              | 各功能独立测试用例实现（完全独立） |

---

# 五、架构核心优势（你最关心的解耦效果）
1. **修改UI → 只动ui/文件夹**
2. **修改ADB功能 → 只动commons/adb_service.py**
3. **新增测试用例 → 只在对应模块添加，零修改核心**
4. **无循环导入、无跨层调用、无冗余代码**
5. **按硬件功能模块化，与RV1126B开发板功能完全对应**
6. **微内核架构，核心稳定，功能可插拔**

---

# ✅ 架构确认完成
这就是**最终、固定、可直接落地开发**的项目文件架构！
完全满足：
- 分层解耦
- USB有线ADB
- 日志/报告统一归档
- 开发单一模块无需修改多个文件
- 测试用例模块化分离
- 新增用例零修改核心代码
- 与RV1126B硬件功能一一对应
- 旧架构已完全迁移并清理

你确认这个架构无问题后，我们就可以**按模块顺序，开始逐步开发**了！
