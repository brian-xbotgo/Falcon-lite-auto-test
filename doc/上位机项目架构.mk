# RV1126B ADB 自动化冒烟测试工具 - 最终整合版项目设计与架构
**版本**：V2.2（2026-04-14 微内核架构完成版）
**核心原则**：分层解耦、高内聚低耦合、USB有线ADB专属、日志/报告统一归档、单一模块修改无交叉、测试用例模块化分离
**✅ 已完成旧架构迁移：engine已整合至commons**

## 一、项目概述
### 1.1 项目名称
RV1126B ADB 自动化冒烟测试工具

### 1.2 项目定位
面向 RV1126B 芯片设备的**USB有线ADB自动化测试上位机**，支持批量自动化测试+人工集中确认、实时日志、测试报告生成、文件管理，全程可追溯、结果可导出。

### 1.3 核心功能
1. USB有线ADB设备扫描、连接、指令执行
2. 全量冒烟测试/部分功能调试双模式
3. 自动化测试优先 + 人工项集中确认
4. 实时分级日志输出，自动保存至本地
5. 测试报告自动生成（Excel/HTML）
6. 固件/日志/报告统一文件管理
7. ✅ 插件化测试用例管理（新增用例零修改核心）

### 1.4 技术栈
- 开发语言：Python 3.10+
- UI框架：PyQt6
- 通信方式：USB ADB（subprocess 封装）
- 数据存储：本地 `data/` 目录
- 报告生成：Excel/HTML
- 架构模式：**微内核插件化架构**

## 二、整体架构设计
### 2.1 分层架构（4层单向依赖，无循环、无跨层调用）
```
UI 展示层 → commons微内核 → 功能插件层 → 数据持久层
```
- **依赖规则**：仅上层调用下层，下层绝不感知上层
- **核心目标**：内核100%稳定，功能模块完全可插拔

### 2.2 分层职责边界
| 层级 | 核心职责 | 禁止操作 |
|------|----------|----------|
| **UI 展示层** | 纯界面渲染、按钮响应、数据展示 | 不写任何ADB/测试/文件业务逻辑 |
| **✅ commons微内核** | 全局公共能力+测试调度引擎 | 不实现任何具体业务测试逻辑 |
| **✅ 功能插件层** | 各硬件功能独立测试用例实现 | 不操作UI、不处理全局调度 |
| **数据持久层** | 唯一数据出口（日志、报告、固件存储） | 不存放代码/配置文件 |

## 三、最终定型目录结构
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
├── commons/                # ✅ 微内核核心（稳定不变）
│   ├── __init__.py         # 统一导出所有公共接口
│   ├── log_service.py      # 日志服务
│   ├── adb_service.py      # ADB基础服务
│   ├── device_model.py     # 设备数据模型
│   ├── test_model.py       # 测试用例数据模型
│   ├── config.py           # 全局配置
│   ├── common.py           # 通用工具函数
│   └── engine/             # ✅ 调度引擎核心（微内核）
│       ├── __init__.py
│       ├── test_service.py # 测试调度引擎 + 自动发现注册
│       └── report_service.py # 报告生成引擎
├── misc/                   # ✅ 功能插件：系统杂项
│   ├── __init__.py
│   └── version_info/       # 版本信息测试用例
│       ├── __init__.py
│       └── test_version_read.py
├── btwifi/                 # ✅ 功能插件：蓝牙+WiFi
│   ├── __init__.py
│   └── network_test/       # 网络测试用例
│       ├── __init__.py
│       └── test_network_connectivity.py
├── bleConfigureWifi/       # ✅ 功能插件：蓝牙配网
│   └── __init__.py
├── ble_central/            # ✅ 功能插件：BLE主机
│   └── __init__.py
├── http_agent/             # ✅ 功能插件：HTTP客户端
│   └── __init__.py
├── mqtt_wrapper/           # ✅ 功能插件：MQTT
│   └── __init__.py
├── ota_update/             # ✅ 功能插件：OTA升级
│   └── __init__.py
├── sdcard_firming/         # ✅ 功能插件：SD卡
│   └── __init__.py
├── lvgl_app/               # ✅ 功能插件：LVGL界面
│   ├── __init__.py
│   ├── charge_lvgl_app/    # 充电状态测试
│   │   └── __init__.py
│   └── normal_lvgl_app/    # 正常状态测试
│       └── __init__.py
├── multi_media/            # ✅ 功能插件：多媒体
│   └── __init__.py
├── stepper_motor_control/  # ✅ 功能插件：步进电机
│   └── __init__.py
├── brushless_motor_control/# ✅ 功能插件：无刷电机
│   └── __init__.py
├── detect/                 # ✅ 功能插件：AI检测
│   └── __init__.py
├── tracking/               # ✅ 功能插件：目标跟踪
│   └── __init__.py
├── stream/                 # ✅ 功能插件：流媒体
│   └── __init__.py
└── data/                   # 数据持久层
    ├── logs/               # 运行日志
    ├── reports/            # 测试报告
    └── firmware/           # 固件包存储
```

## 四、✅ 插件化开发规范（重点！新增用例零修改核心）
### 新增测试用例标准流程（3步，零修改内核）：
```
1. 在对应功能模块下创建子文件夹（如：btwifi/ssid_scan/）
2. 创建测试文件：test_xxx.py
3. 实现测试函数并添加装饰器：
   @register_test_case("A003")
   def test_xxx(device_serial: str) -> tuple[bool, str]:
       # 测试逻辑
       return success, message
```

### 人工测试复位命令支持
对于需要执行测试命令后等待观察，确认后自动复位的测试用例，支持返回三元组格式：
```python
@register_test_case("B005")
def test_motor(device_serial: str) -> tuple[None, str, str]:
    # 执行测试命令
    ADBService.exec_shell(device_serial, test_cmd)
    # 返回：(状态, 提示信息, 复位命令)
    return None, "请观察电机运动", reset_cmd
```
- 状态为`None`表示等待人工确认
- 测试引擎在用户点击"确认通过"后**自动执行复位命令**
- 无需在测试函数中处理复位逻辑，也无需修改引擎代码

### 命令编写重要规范
✅ **所有包含`\x`十六进制转义的命令必须使用原始字符串**：
```python
# ✅ 正确：使用r前缀，转义序列完整传递到设备shell
test_cmd = r'''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''

# ❌ 错误：Python会提前解析\x字符，导致命令失效
test_cmd = '''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
```
- 该规则适用于所有printf/echo/MQTT命令
- 引擎会自动处理命令转义，防止Windows本地shell解析特殊字符

### 自动发现机制：
- 引擎启动时自动扫描所有功能模块目录
- 自动注册所有带 `@register_test_case` 装饰器的函数
- 无需修改任何核心代码，完全解耦

## 五、核心模块定义
### 5.1 commons微内核（永远稳定，不修改）
| 文件 | 核心功能 |
|------|----------|
| `log_service.py` | 分级日志输出、自动写入文件 |
| `adb_service.py` | USB设备扫描、ADB指令执行 |
| `device_model.py` | 设备数据模型定义 |
| `test_model.py` | 测试用例数据模型定义 |
| `config.py` | 全局配置参数 |
| `common.py` | 通用工具函数 |
| `engine/test_service.py` | 测试用例调度、自动发现注册 |
| `engine/report_service.py` | 测试报告生成、保存 |

### 5.2 功能插件层（可插拔，独立开发）
| 模块 | 对应硬件功能 |
|------|----------|
| `misc/` | 系统杂项测试 |
| `btwifi/` | 蓝牙+WiFi测试 |
| `bleConfigureWifi/` | 蓝牙配网测试 |
| `ble_central/` | BLE主机测试 |
| `http_agent/` | HTTP客户端测试 |
| `mqtt_wrapper/` | MQTT通信测试 |
| `ota_update/` | OTA升级测试 |
| `sdcard_firming/` | SD卡功能测试 |
| `lvgl_app/` | LVGL界面测试 |
| `multi_media/` | 多媒体功能测试 |
| `stepper_motor_control/` | 步进电机测试 |
| `brushless_motor_control/` | 无刷电机测试 |
| `detect/` | AI检测功能测试 |
| `tracking/` | 目标跟踪测试 |
| `stream/` | 流媒体传输测试 |

## 六、核心业务流程
1. 启动工具 → 自动扫描并注册所有测试用例
2. 扫描USB-ADB设备 → 选中设备
3. 勾选测试项 → 开始测试
4. 引擎调度执行测试用例 → 自动执行所有自动化项
5. 自动化完成 → 暂停等待人工确认
6. 人工确认完成 → 自动生成报告
7. 所有结果保存至 `data/` 目录

## 七、代码规范
### 测试用例规范：
- 文件命名：`test_xxx.py`
- 函数命名：`test_xxx(device_serial: str) -> tuple[bool, str]`
- ✅ **测试ID规范**：
  - `Axxx` = 自动化测试用例（优先执行）
  - `Bxxx` = 人工测试用例（自动化全部完成后执行）
  - xxx为3位数字自增编号
- 必须使用 `@register_test_case("测试ID")` 装饰器
- 只依赖 `commons` 导出的公共接口
- 不处理任何调度逻辑，只实现测试本身
- 引擎自动排序：先执行所有A类，再执行所有B类

## 八、项目核心优势
1. **微内核架构**：核心永远稳定，功能模块完全可插拔
2. **零修改新增**：新增测试用例不需要修改任何核心代码
3. **彻底解耦**：模块间无依赖，单一模块开发不影响其他
4. **硬件对齐**：功能模块与RV1126B硬件功能一一对应
5. **易维护**：分层清晰、职责明确、结构稳定
6. **可扩展**：新增功能只需新增插件，无需改动现有代码
7. **多设备支持**：支持Chameleon/Falcon/Falcon-Air三种设备类型
8. **智能过滤**：测试用例可声明支持的设备类型，不支持项自动跳过
9. **准确统计**：不支持项不计入通过率，统计结果准确
