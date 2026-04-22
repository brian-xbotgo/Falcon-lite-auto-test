# RV1126B 测试工具 - 增减测试用例教程
**版本**：V1.3（2026-04-14）
**适用架构**：微内核插件化架构
**核心优势**：✅ 新增/删除测试用例 **零修改核心代码**，完全插件化
**✅ 最新特性**：
- 文件预览双击重复打开问题已修复
- 部分测试页单步执行选中用例功能已修复
- ✅ ✅ 全自动编号系统实现：只需要标记A/B，编号自动自增
- ✅ 测试用例编号规范已实现：A=自动化，B=人工，自动排序执行

---

## 📋 前言
本项目采用 **微内核插件化架构**，测试用例完全独立于核心调度引擎。
- ✅ 新增测试用例：不需要修改任何核心文件
- ✅ 删除测试用例：不需要修改任何核心文件
- ✅ 所有测试用例自动发现、自动注册

---

## ➕ 新增测试用例完整教程（3步完成）

### 第1步：确定测试用例所属功能模块
根据测试功能选择对应的模块文件夹：

| 测试功能 | 对应模块目录 |
|----------|--------------|
| 系统/版本/杂项 | `misc/` |
| 蓝牙/WiFi/网络 | `btwifi/` |
| 蓝牙配网 | `bleConfigureWifi/` |
| BLE主机 | `ble_central/` |
| HTTP客户端 | `http_agent/` |
| MQTT通信 | `mqtt_wrapper/` |
| OTA升级 | `ota_update/` |
| SD卡功能 | `sdcard_firming/` |
| LVGL界面 | `lvgl_app/` |
| 多媒体/音视频 | `multi_media/` |
| 步进电机 | `stepper_motor_control/` |
| 无刷电机 | `brushless_motor_control/` |
| AI检测/识别 | `detect/` |
| 目标跟踪 | `tracking/` |
| 流媒体/推流 | `stream/` |

### 第2步：在对应模块下创建子文件夹
每个测试用例一个独立文件夹：
```bash
# 示例：新增一个WiFi扫描测试用例
mkdir btwifi/ssid_scan
```

### 第3步：创建测试文件并实现测试逻辑
在新建的文件夹中创建测试文件，命名规范：`test_xxx.py`

#### ✅ 标准测试用例模板（复制即可用）：
```python
# -*- coding: utf-8 -*-
"""
测试用例A003：WiFi扫描测试
功能：扫描周边WiFi热点
作者：你的名字
创建时间：2026-04-14
"""
from commons import ADBService, log, register_test_case, Priority, Module


@register_test_case("A", name="WiFi扫描测试", module=Module.BTWIFI, priority=Priority.P0, supported_devices=[2, 3])  
                             # ✅ 必须添加此装饰器，完整参数示例
                             # 
                             # 📌 完整参数说明：
                             # @register_test_case(类型标记, 名称, 模块, 优先级, supported_devices)
                             # 📌 ✅ 模块参数现在推荐使用 Module 枚举：
                             # - Module.MISC = 系统杂项
                             # - Module.BTWIFI = 蓝牙WiFi
                             # - Module.BLE_CONFIGURE_WIFI = 蓝牙配网
                             # - Module.BLE_CENTRAL = BLE主机
                             # - Module.HTTP_AGENT = HTTP客户端
                             # - Module.MQTT_WRAPPER = MQTT通信
                             # - Module.OTA_UPDATE = OTA升级
                             # - Module.SDCARD_FIRMING = SD卡功能
                             # - Module.LVGL_APP = LVGL界面
                             # - Module.MULTI_MEDIA = 多媒体
                             # - Module.STEPPER_MOTOR = 步进电机
                             # - Module.BRUSHLESS_MOTOR = 无刷电机
                             # - Module.DETECT = AI检测
                             # - Module.TRACKING = 目标跟踪
                             # - Module.STREAM = 流媒体
                             # 
                             # 📌 ✅ 全自动编号系统！你只需要标记A/B：
                             # - 标记 'A' = 自动化测试用例（优先执行）
                             # - 标记 'B' = 人工测试用例（自动化全部完成后执行）
                             # 
                             # 📌 ✅ 优先级说明：
                             # - Priority.P0 = 最高优先级（冒烟核心用例）
                             # - Priority.P1 = 高优先级
                             # - Priority.P2 = 中优先级
                             # - Priority.P3 = 低优先级
                             # - Priority.P4 = 最低优先级
                             # 同类型测试用例按优先级从高到低执行
                             # 
                             # 📌 ✅ 设备类型过滤：
                             # - supported_devices = [1] → 仅支持Chameleon
                             # - supported_devices = [2, 3] → 支持Falcon和Falcon-Air
                             # - supported_devices = None → 支持所有设备(默认)
                             # 
                             # ✅ 系统自动处理所有编号：
                             # 1. 自动检测是第几个A/B类型的用例
                             # 2. 自动生成编号：A001, A002, B001, B002...
                             # 3. 自动按【类型→优先级→编号】正确顺序排序执行
                             # 
                             # ✅ 你不需要记忆和编写数字编号！
                             # 示例（人工测试用例）：
                             # @register_test_case("B", name="按键测试", module="硬件", priority=Priority.P1, supported_devices=[1])
def test_wifi_ssid_scan(device_serial: str) -> tuple[bool, str]:
    """
    测试用例A003：WiFi扫描测试
    :param device_serial: 设备序列号
    :return: (测试结果:True/False, 测试消息/备注)
    """
    log.debug("执行WiFi扫描测试")
    
    # 测试逻辑示例（根据实际需求修改）
    success, output = ADBService.exec_shell(
        device_serial,
        "wpa_cli scan_results",
        timeout=30
    )

    if success and output:
        # 测试通过
        return True, f"扫描到 {len(output.splitlines())} 个WiFi热点"
    else:
        # 测试失败
        return False, output
```

### ✅ 测试用例编号规范（重要！✅ 全自动编号）
| 标记 | 类型 | 执行顺序 |
|------|------|----------|
| `"A"` | 自动化测试用例 | ✅ 优先执行，所有A类用例执行完成后才会执行B类 |
| `"B"` | 人工测试用例 | ✅ 所有自动化完成后执行 |

- ✅ **你只需要标记A或B**，不需要写数字
- ✅ 系统自动检测第几个A/B用例
- ✅ 自动生成编号：A001, A002, B001, B002...
- ✅ 自动按正确顺序排序执行

### 示例：
```python
@register_test_case("A", name="版本信息读取", ...)  # 自动分配 A001
@register_test_case("A", name="网络连通性测试", ...) # 自动分配 A002
@register_test_case("B", name="LED指示灯检查", ...)  # 自动分配 B001
@register_test_case("B", name="屏幕显示观察", ...)  # 自动分配 B002
```

## ✅ 测试用例编写规范（必须遵守）
1. **文件命名**：必须以 `test_` 开头，`.py` 结尾
2. **函数签名**：
   - 普通测试：`def test_xxx(device_serial: str) -> tuple[bool, str]:`
   - 带复位的人工测试：`def test_xxx(device_serial: str) -> tuple[bool | None, str, str]:`
3. **装饰器**：必须添加 `@register_test_case()` 装饰器
4. **返回值格式**：
   - `(True, 消息)` = 自动化测试通过
   - `(False, 错误消息)` = 自动化测试失败
   - `(None, 提示消息)` = 等待人工确认
   - `(None, 提示消息, 复位命令)` = 等待人工确认，确认通过后自动执行复位命令
5. **依赖**：只能从 `commons` 导入公共接口，不能导入其他模块的内部实现
6. **设备类型过滤**：使用 `supported_devices` 参数声明支持的设备类型
   - `supported_devices=[1]` - 仅支持Chameleon
   - `supported_devices=[2,3]` - 仅支持Falcon/Falcon-Air
   - 不写此参数表示支持所有设备
7. **工具文件使用**：测试用例需要的二进制工具放在 `tools/` 目录下，使用 `ADBService.push_and_prepare_tool()` 方法上传到设备

## ✅ 人工测试自动复位功能（2026-04-17新增）
对于电机、LED等需要执行测试命令后等待观察，确认后自动复位的场景：

```python
@register_test_case("B", name="水平电机测试", module="步进电机", priority="P0")
def test_horizontal_motor(device_serial: str) -> tuple[None, str, str]:
    # 1. 执行测试命令
    test_cmd = r'''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
    success, output = ADBService.exec_shell(device_serial, test_cmd)
    
    if not success:
        return False, f"电机测试命令失败: {output}"
    
    # 2. 返回三元组：(None, 提示信息, 复位命令)
    reset_cmd = r'''printf '\x00\x62\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
    return None, "请观察水平电机运动是否正常", reset_cmd
```

✅ **引擎自动处理流程**：
1. 执行测试命令 → 2. 显示等待人工确认 → 3. 用户点击确认通过 → **4. 引擎自动执行复位命令** → 5. 测试标记为通过

## ✅ 十六进制命令编写强制规范
**所有包含`\x`十六进制转义的字符串必须使用**原始字符串**（r前缀）：

✅ 正确：
```python
test_cmd = r'''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
```
❌ 错误（严重错误，会导致命令失效：
```python
test_cmd = '''printf '\x00\x66\x20\x03\x00\x06' | mosquitto_pub -h localhost -t "A" -s'''
```

- 规则说明：
- 不加r前缀时，Python会提前解析`\x00`解析为空字符，导致shell收到的命令丢失转义序列丢失
- 引擎已自动处理命令转义，防止Windows shell解析`|`、`>`等特殊字符
- 该规范适用于所有printf/echo/MQTT二进制命令

---

## 🔍 测试用例自动注册+自动排序机制
- 程序启动时自动扫描所有功能模块目录
- 自动查找所有 `test_*.py` 文件
- 自动注册所有带 `@register_test_case` 装饰器的函数
- ✅ **自动排序**：引擎自动按测试ID排序，先执行所有A类自动化用例，再执行所有B类人工用例
- 无需修改任何核心代码，无需手动导入，无需手动排序

---

## ➖ 删除测试用例
**只需要1步**，不需要修改任何核心代码：
```bash
# 直接删除测试用例文件夹即可
rm -rf btwifi/ssid_scan
```

程序启动时会自动忽略已删除的测试用例，完全不需要清理任何注册信息。

---

## ✅ 验证测试用例是否生效
1. 启动程序
2. 查看控制台日志，搜索"注册测试用例"
3. 如果看到类似日志，说明注册成功：
   ```
   [时间] | DEBUG   | 注册测试用例: A003 -> test_wifi_ssid_scan
   ```
4. 在全部测试页面可以看到新增的测试用例

---

## 📌 完整示例：新增测试用例全过程
### 需求：新增"版本信息读取"测试用例
```bash
# 1. 创建文件夹
mkdir misc/version_info

# 2. 创建测试文件 misc/version_info/test_version_read.py
```

```python
# misc/version_info/test_version_read.py
from commons import ADBService, DEFAULT_TEST_TIMEOUT, log, register_test_case


@register_test_case("A001")
def test_version_read(device_serial: str) -> tuple[bool, str]:
    """测试用例A001：读取设备版本号"""
    log.debug("读取设备版本文件: /oem/usr/bin/version.txt")
    success, output = ADBService.exec_shell(
        device_serial,
        "cat /oem/usr/bin/version.txt",
        timeout=DEFAULT_TEST_TIMEOUT
    )

    if success and output.strip():
        return True, f"版本号: {output.strip()}"
    elif success:
        return False, "版本文件为空"
    else:
        log.debug("尝试通用版本获取方式")
        success2, output2 = ADBService.exec_shell(device_serial, "cat /proc/version")
        if success2 and output2.strip():
            return True, f"内核版本: {output2.strip()[:100]}..."
        return False, output
```

✅ **完成！不需要修改任何其他文件，程序启动自动发现并注册**

---

## ❓ 常见问题
### Q: 新增测试用例后需要重启程序吗？
A: 需要，测试用例只在程序启动时扫描一次。

### Q: 测试用例之间可以互相调用吗？
A: 不建议，每个测试用例应该独立。如果需要共享逻辑，提取到commons中。

### Q: 测试ID可以重复吗？
A: 不可以，每个测试用例必须有唯一的测试ID。

### Q: 测试用例需要添加到_init_test_cases吗？
A: 不需要！✅ 自动发现机制会处理，完全不需要修改test_service.py。

---

## ✅ 测试工具上传方法（2026-04-21新增）
对于需要使用外部工具的测试用例，使用封装好的工具上传方法：
```python
# 上传工具到设备/tmp目录并自动添加执行权限
success, remote_path = ADBService.push_and_prepare_tool(
    device_serial,
    "tools/record_tool/record_test"
)
if success:
    # 运行工具
    ADBService.exec_shell(device_serial, f"{remote_path} --test")
```

## ⚠️ 注意事项
1. ❌ 不要修改 `commons/engine/` 下的任何文件
2. ❌ 不要手动在test_service.py中硬编码测试用例
3. ✅ 所有测试逻辑都应该放在对应的功能模块文件夹中
4. ✅ 测试用例只依赖commons导出的公共接口
5. ✅ 静态工具文件放在 `tools/` 目录下，随程序打包
