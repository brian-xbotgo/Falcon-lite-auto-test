# RV1126B Test Tool

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](LICENSE)

English | [中文](./README.md)

🚀 **Automated Smoke Testing Tool for RV1126B/RK3576 Devices**

A specialized USB ADB automated testing tool designed for RV1126B/RK3576 chip devices, supporting batch automated testing, real-time logging, test report generation, and file management.

## ✨ Key Features

### 🎯 Testing Capabilities
- **🔌 USB ADB Testing** - Stable device connection via ADB
- **🤖 Automated Testing** - Support for 20+ automated test cases
- **👥 Manual Assisted Testing** - Intelligent human-AI collaborative testing
- **📊 Real-time Monitoring** - Hierarchical logging and status tracking
- **📋 Auto Reporting** - Excel/HTML/Table test report generation
- **📡 Device Scanning** - Bluetooth + WiFi dual-mode scanning, quick discovery of Xb devices

### 🏗️ Architecture Advantages
- **🔧 Microkernel Design** - Stable core with pluggable features
- **📦 Modular Management** - Zero core modification for new test cases
- **🔄 Device Compatibility** - Support for Chameleon/Falcon/Falcon-Air
- **⚡ High Performance** - Asynchronous processing and multi-threading
- **📡 Dual-mode Scanning** - Bluetooth and WiFi scanning unified interface, flexible adaptation

### 🎮 Function Modules
- **📹 Multimedia Testing** - Video recording, audio recording, photo capture, recording marks, auto tracking, scoreboard watermark, electronic fence, 1080P/2K recording
- **🔧 Hardware Control** - Motor control, LED control, buzzer testing
- **📱 Device Management** - SD card detection, version info, screen testing
- **🔗 Network Features** - WiFi, Bluetooth, MQTT communication testing
- **📡 Device Scanning** - Support Bluetooth and WiFi dual-mode scanning, automatic identification of Xb devices

## 🚀 Quick Start

### 📋 System Requirements

- **OS**: Windows 10/11, Ubuntu 20.04+
- **Python**: 3.10 or higher
- **ADB**: Android Debug Bridge (included in Android SDK)
- **Hardware**: RV1126B/RK3576 development board

### ⚡ Installation

#### 1. Clone the repository
```bash
git clone https://github.com/your-username/RV1126B_Test_Tool.git
cd RV1126B_Test_Tool
```

#### 2. Create virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the tool
```bash
python main.py
```

### 🛠️ ADB Environment Configuration

Ensure ADB tools are available:
```bash
# Check ADB installation
adb version

# If not installed, download Android SDK Platform Tools
# https://developer.android.com/studio/releases/platform-tools
```

## 📖 Usage Guide

### 🎯 Basic Operations

1. **Connect Device**
   - Connect RV1126B/RK3576 development board via USB
   - Ensure device has ADB debugging enabled

2. **Scan Devices**
   - Tool will automatically scan connected ADB devices
   - Select target device from device list

3. **Select Tests**
   - **All Tests**: Execute all available test cases
   - **Partial Tests**: Select specific test cases for execution

4. **View Results**
   - Real-time view of test progress and logs
   - Generate complete test reports

### 📊 Test Cases

| Category | Test Case | Type | Status |
|----------|----------|------|--------|
| Multimedia | Video Recording Test | Auto | ✅ |
| Multimedia | Audio Recording Test | Auto | ✅ |
| Multimedia | Photo Capture Test | Auto | ✅ |
| Multimedia | M-Key Recording Test | Auto | ✅ |
| Multimedia | Recording Mark Test | Auto | ✅ |
| Multimedia | Auto Tracking Test | Auto | ✅ |
| Multimedia | Scoreboard & Watermark Test | Auto | ✅ |
| Multimedia | Electronic Fence Test | Auto | ✅ |
| Multimedia | 1080P30fps Recording Test | Auto | ✅ |
| Multimedia | 2K30fps Recording Test | Auto | ✅ |
| Multimedia | Live Streaming Test | Manual | ✅ |
| Hardware | Horizontal Motor Test | Auto | ✅ |
| Hardware | Pitch Motor Test | Auto | ✅ |
| System | SD Card Check | Auto | ✅ |
| System | Version Info Read | Auto | ✅ |
| System | LED Indicator Check | Manual | ✅ |
| System | Buzzer Test | Manual | ✅ |

### 📁 File Management

- **Log Files**: `data/logs/` - Runtime logs and operation records
- **Test Reports**: `data/reports/` - Excel/HTML/Table format reports
- **Firmware Files**: `data/firmware/` - Firmware update package storage

## 📚 Documentation

### 🏛️ Architecture Documentation
- **[Architecture Overview](./doc/architecture/overview_EN.md)** - Complete architecture design
- **[Design Specifications](./doc/architecture/design_EN.md)** - Code standards and development guidelines
- **[Plugin System](./doc/development/plugin_system_EN.md)** - Test case plugin development guide

### 👨‍💻 Development Documentation
- **[Getting Started](./doc/development/getting_started_EN.md)** - Development setup guide
- **[API Reference](./doc/development/api_reference_EN.md)** - Detailed API documentation
- **[Testing Guide](./doc/development/testing_guide_EN.md)** - Unit and integration testing
- **[Deployment Guide](./doc/deployment/deployment_EN.md)** - Production environment deployment

### 📖 User Documentation
- **[Installation](./doc/user_guide/installation_EN.md)** - Detailed installation and configuration
- **[User Manual](./doc/user_guide/manual_EN.md)** - Complete usage guide
- **[Troubleshooting](./doc/user_guide/troubleshooting_EN.md)** - Common issues and solutions

## 🤝 Contributing

We welcome all forms of contribution! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### 🚀 Quick Contribution

1. **Fork** this project
2. **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Create** a Pull Request

### 🐛 Reporting Issues

- Use [GitHub Issues](https://github.com/your-username/RV1126B_Test_Tool/issues) to report bugs
- Provide detailed error information and reproduction steps
- For feature requests, describe specific usage scenarios

## 📋 Version History

Check [CHANGELOG.md](./CHANGELOG.md) for detailed version change information.

### Latest Version: v2.5 (2026-04-30)

- ✨ Added WiFi scanning feature (support Xb hotspot scanning)
- 🔧 Optimized M-key recording test to automated
- 🛠️ UI optimization: separate scan buttons, no auto-scan after disconnect
- 📦 Dependency update: added pywifi>=1.1.12 and comtypes>=1.1.7
- 📚 Documentation: packaging guide, architecture specs, service layer design

### Previous Version: v2.4 (2026-04-27)

- ✨ Added recording mark automated test
- 🔧 Optimized M-key recording test to automated
- 🛠️ Improved device-side time verification mechanism
- 📱 Enhanced multi-device compatibility

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

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

## 🙏 Acknowledgments

Thanks to all contributors to this project!

Special thanks to:
- RV1126B/RK3576 development team
- Open source community supporters
- All users who provided testing and feedback

## 📞 Contact Us

- **Project Home**: https://github.com/your-username/RV1126B_Test_Tool
- **Issue Tracker**: [GitHub Issues](https://github.com/your-username/RV1126B_Test_Tool/issues)
- **Email**: your-email@example.com

---
⭐ If this project helps you, please give us a star!
