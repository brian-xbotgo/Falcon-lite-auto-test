# RV1126B Test Tool

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](LICENSE)

[English](./README_EN.md) | 中文

🚀 **RV1126B/RK3576 芯片设备自动化冒烟测试上位机工具**

一款专为RV1126B/RK3576芯片设备设计的USB有线ADB自动化测试工具，支持批量自动化测试、实时日志、测试报告生成等功能。

## ✨ 核心特性

### 🎯 测试能力
- **🔌 USB有线ADB测试** - 稳定可靠的设备连接
- **🤖 自动化测试** - 支持10+自动化测试用例
- **👥 人工辅助测试** - 智能的人机协作测试模式
- **📊 实时监控** - 分级日志输出和状态跟踪
- **📋 自动报告** - Excel/HTML格式测试报告生成

### 🏗️ 架构优势
- **🔧 微内核设计** - 核心稳定，功能插件化
- **📦 模块化管理** - 测试用例零修改核心代码
- **🔄 设备兼容** - 支持Chameleon/Falcon/Falcon-Air多设备
- **⚡ 高性能** - 异步处理和多线程支持

### 🎮 功能模块
- **📹 多媒体测试** - 视频录制、音频录制、拍照、录制打点
- **🔧 硬件控制** - 电机控制、LED控制、蜂鸣器测试
- **📱 设备管理** - SD卡检测、版本信息、屏幕测试
- **🔗 网络功能** - WiFi、蓝牙、MQTT通信测试

## 🚀 快速开始

### 📋 环境要求

- **操作系统**: Windows 10/11, Ubuntu 20.04+
- **Python**: 3.10 或更高版本
- **ADB**: Android Debug Bridge (包含在Android SDK中)
- **硬件**: RV1126B/RK3576开发板

### ⚡ 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-username/RV1126B_Test_Tool.git
cd RV1126B_Test_Tool
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 运行工具
```bash
python main.py
```

### 🛠️ ADB环境配置

确保ADB工具可用：
```bash
# 检查ADB安装
adb version

# 如果未安装，请下载Android SDK Platform Tools
# https://developer.android.com/studio/releases/platform-tools
```

## 📖 使用指南

### 🎯 基本操作

1. **连接设备**
   - 通过USB连接RV1126B/RK3576开发板
   - 确保设备已开启ADB调试模式

2. **扫描设备**
   - 工具会自动扫描连接的ADB设备
   - 在设备列表中选择目标设备

3. **选择测试**
   - **全部测试**: 执行所有可用测试用例
   - **部分测试**: 选择特定测试用例执行

4. **查看结果**
   - 实时查看测试进度和日志
   - 生成完整的测试报告

### 📊 测试用例

| 分类 | 测试用例 | 类型 | 状态 |
|------|----------|------|------|
| 多媒体 | 视频录制测试 | 自动 | ✅ |
| 多媒体 | 音频录制测试 | 自动 | ✅ |
| 多媒体 | 拍照功能测试 | 自动 | ✅ |
| 多媒体 | M键录像测试 | 自动 | ✅ |
| 多媒体 | 录制打点测试 | 自动 | ✅ |
| 硬件 | 水平电机测试 | 自动 | ✅ |
| 硬件 | 俯仰电机测试 | 自动 | ✅ |
| 系统 | SD卡检查 | 自动 | ✅ |
| 系统 | 版本信息读取 | 自动 | ✅ |
| 系统 | LED指示灯检查 | 人工 | ✅ |
| 系统 | 蜂鸣器测试 | 人工 | ✅ |

### 📁 文件管理

- **日志文件**: `data/logs/` - 运行日志和操作记录
- **测试报告**: `data/reports/` - Excel/HTML格式报告
- **固件文件**: `data/firmware/` - 固件更新包存储

## 📚 文档

### 🏛️ 架构文档
- **[项目架构](./doc/上位机项目架构.mk)** - 整体架构设计和分层说明
- **[架构规范](./doc/架构规范.mk)** - 代码规范和开发标准
- **[插件系统](./doc/增减测试用例教程.mk)** - 测试用例插件化开发指南

### 👨‍💻 开发文档
- **[API参考](./doc/api_reference.md)** - 详细的API文档
- **[测试指南](./doc/testing_guide.md)** - 单元测试和集成测试
- **[部署指南](./doc/deployment.md)** - 生产环境部署说明

### 📖 用户文档
- **[安装指南](./doc/installation.md)** - 详细的安装和配置说明
- **[使用手册](./doc/user_manual.md)** - 完整的使用指南
- **[故障排除](./doc/troubleshooting.md)** - 常见问题和解决方案

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解详细信息。

### 🚀 快速贡献

1. **Fork** 本项目
2. **创建** 你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **创建** Pull Request

### 🐛 报告问题

- 使用 [GitHub Issues](https://github.com/your-username/RV1126B_Test_Tool/issues) 报告bug
- 提供详细的错误信息和复现步骤
- 建议功能时请描述具体的使用场景

## 📋 项目结构

```
RV1126B_Test_Tool/
├── main.py                 # 🏁 程序入口
├── ui/                     # 🎨 用户界面层
│   ├── main_window.py      # 主窗口
│   ├── tab_all_test.py     # 全部测试页面
│   ├── tab_part_test.py    # 部分测试页面
│   └── tab_log_view.py     # 日志查看页面
├── commons/                # ⚙️ 微内核核心
│   ├── __init__.py         # 公共接口导出
│   ├── adb_service.py      # ADB服务
│   ├── test_service.py     # 测试调度引擎
│   ├── report_service.py   # 报告生成服务
│   └── engine/             # 测试引擎核心
├── multi_media/            # 📹 多媒体测试模块
│   ├── camera_test/        # 摄像头测试
│   ├── audio_test/         # 音频测试
│   └── record_misc/        # 录制杂项测试
├── misc/                   # 🔧 系统杂项测试
│   ├── version_info/       # 版本信息
│   ├── screen_test/        # 屏幕测试
│   └── battery/            # 电池测试
├── stepper_motor_control/  # 🤖 步进电机控制
├── tools/                  # 🛠️ 工具文件
│   ├── shell_script/       # Shell脚本
│   └── record_tool/        # 录制工具
├── doc/                    # 📚 项目文档
├── data/                   # 💾 运行时数据
│   ├── logs/               # 日志文件
│   ├── reports/            # 测试报告
│   └── firmware/           # 固件包
└── requirements.txt        # 📦 Python依赖
```

## 🔄 版本历史

查看 [CHANGELOG.md](./CHANGELOG.md) 了解详细的版本变更信息。

### 最新版本: v2.4 (2026-04-27)

- ✨ 新增录制打点自动化测试
- 🔧 优化M键录像测试为自动化
- 🛠️ 改进设备端时间验证机制
- 📱 增强多设备兼容性

## 📄 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

```
Copyright 2026 RV1126B_Test_Tool Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

特别感谢：
- RV1126B/RK3576 开发团队
- 开源社区的支持者
- 所有测试和反馈的用户

## 📞 联系我们

- **项目主页**: https://github.com/your-username/RV1126B_Test_Tool
- **问题反馈**: [GitHub Issues](https://github.com/your-username/RV1126B_Test_Tool/issues)
- **邮箱**: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个star！