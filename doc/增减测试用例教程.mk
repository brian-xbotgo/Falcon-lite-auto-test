# RV1126B 测试工具 - 增减测试用例教程
**版本**：V1.2（2026-04-14）
**适用架构**：微内核插件化架构
**核心优势**：✅ 新增/删除测试用例 **零修改核心代码**，完全插件化
**✅ 最新特性**：
- 文件预览双击重复打开问题已修复
- 部分测试页单步执行选中用例功能已修复
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
from commons import ADBService, log, register_test_case


@register_test_case("A003")  # ✅ 必须添加此装饰器，参数为测试ID
                             # 📌 编号规范：
                             # - A开头：自动化测试用例（优先执行）
                             # - B开头：人工测试用例（自动化全部完成后执行）
                             # - 后面3位数字：按顺序自增，同类用例按编号顺序执行
                             # 
                             # ✅ 引擎自动保证：
                             # 1. 先执行所有Axxx自动化用例
                             # 2. 再执行所有Bxxx人工用例
                             # 3. 同类用例按编号从小到大顺序执行
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

### ✅ 测试用例编号规范（重要！）
| 前缀 | 类型 | 执行顺序 |
|------|------|----------|
| `A` | 自动化测试用例 | ✅ 优先执行，所有A类用例执行完成后才会执行B类 |
| `B` | 人工测试用例 | ✅ 所有自动化完成后执行 |

- **编号格式**：`Axxx` 或 `Bxxx`，xxx为3位数字
- **自增规则**：同类用例按数字顺序自增
- **执行顺序**：引擎自动排序，先A后B，同类按编号从小到大

### 示例：
```
A001 版本信息读取（自动化，第一个执行）
A002 网络连通性测试（自动化，第二个执行）
B001 LED指示灯检查（人工，自动化全部完成后执行）
B002 屏幕显示观察（人工，最后执行）
```

## ✅ 测试用例编写规范（必须遵守）
1. **文件命名**：必须以 `test_` 开头，`.py` 结尾
2. **函数签名**：必须是 `def test_xxx(device_serial: str) -> tuple[bool, str]:`
3. **装饰器**：必须添加 `@register_test_case("测试ID")`
4. **返回值**：第一个是bool表示是否通过，第二个是字符串备注信息
5. **依赖**：只能从 `commons` 导入公共接口，不能导入其他模块的内部实现

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

## ⚠️ 注意事项
1. ❌ 不要修改 `commons/engine/` 下的任何文件
2. ❌ 不要手动在test_service.py中硬编码测试用例
3. ✅ 所有测试逻辑都应该放在对应的功能模块文件夹中
4. ✅ 测试用例只依赖commons导出的公共接口
