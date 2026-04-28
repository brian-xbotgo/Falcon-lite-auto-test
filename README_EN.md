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
- **🤖 Automated Testing** - Support for 10+ automated test cases
- **👥 Manual Assisted Testing** - Intelligent human-AI collaborative testing
- **📊 Real-time Monitoring** - Hierarchical logging and status tracking
- **📋 Auto Reporting** - Excel/HTML test report generation

### 🏗️ Architecture Advantages
- **🔧 Microkernel Design** - Stable core with pluggable features
- **📦 Modular Management** - Zero core modification for new test cases
- **🔄 Device Compatibility** - Support for Chameleon/Falcon/Falcon-Air
- **⚡ High Performance** - Asynchronous processing and multi-threading

### 🎮 Function Modules
- **📹 Multimedia Testing** - Video recording, audio recording, photo capture, recording marks
- **🔧 Hardware Control** - Motor control, LED control, buzzer testing
- **📱 Device Management** - SD card detection, version info, screen testing
- **🔗 Network Features** - WiFi, Bluetooth, MQTT communication testing

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

## 📖 Documentation

### 🏛️ Architecture
- **[Architecture Overview](./doc/architecture/overview_EN.md)** - Complete architecture design
- **[Design Specifications](./doc/architecture/design_EN.md)** - Code standards and development guidelines
- **[Plugin System](./doc/development/plugin_system_EN.md)** - Test case plugin development guide

### 👨‍💻 Development
- **[Getting Started](./doc/development/getting_started_EN.md)** - Development setup guide
- **[API Reference](./doc/development/api_reference_EN.md)** - Detailed API documentation
- **[Testing Guide](./doc/development/testing_guide_EN.md)** - Unit and integration testing

### 📖 User Guide
- **[Installation](./doc/user_guide/installation_EN.md)** - Detailed installation instructions
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

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

## 🙏 Acknowledgments

Thanks to all contributors to this project!

Special thanks to:
- RV1126B/RK3576 development team
- Open source community supporters
- All users who provided testing and feedback

## 📞 Contact

- **Project Home**: https://github.com/your-username/RV1126B_Test_Tool
- **Issue Tracker**: [GitHub Issues](https://github.com/your-username/RV1126B_Test_Tool/issues)
- **Email**: your-email@example.com

---

⭐ If this project helps you, please give us a star!