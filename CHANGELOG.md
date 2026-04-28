# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete English documentation translation
- GitHub Actions CI/CD pipeline
- Issue and PR templates
- Development environment setup guide

### Changed
- Updated README with comprehensive installation and usage guides
- Improved project structure documentation
- Enhanced contributing guidelines

### Fixed
- Device time synchronization issues in automated tests
- File timestamp validation for Android compatibility

## [2.4] - 2026-04-28

### Added
- ✨ **New Test Case**: Recording mark test (`test_record_mark_test.py`)
- 🎯 **Automated Testing**: M-button recording test converted to automated
- 🔧 **MQTT Integration**: Wake-up test with MQTT command sending
- 📱 **Device Compatibility**: Enhanced support for Chameleon/Falcon/Falcon-Air
- ⏰ **Time Validation**: Device-side file timestamp verification
- 📊 **Test Statistics**: 10 automated test cases now supported

### Changed
- 🔄 **Architecture**: Improved microkernel plugin system
- 📈 **Performance**: Optimized ADB communication and file operations
- 🎨 **UI**: Enhanced test progress visualization and logging

### Fixed
- 🐛 **Time Sync Issues**: Resolved device-PC time synchronization problems
- 📁 **File Validation**: Fixed Android timestamp parsing compatibility
- 🔧 **Error Handling**: Improved exception handling in test execution

### Technical Improvements
- Added device timestamp validation mechanism
- Implemented filename-based time parsing as fallback
- Enhanced cross-platform compatibility for Android devices
- Optimized test execution flow and error recovery

## [2.3] - 2026-04-15

### Added
- Device file manager with upload/download capabilities
- Device log one-click packaging and download
- Enhanced multi-device type support
- Improved test case execution statistics

### Changed
- Restructured commons module for better organization
- Updated test service with improved plugin discovery
- Enhanced logging system with cross-thread safety

### Fixed
- Qt cross-thread logging crashes
- Bleak BLE scanning concurrency issues
- QTableWidget DPI scaling artifacts
- Qt deleteLater() dangling pointer crashes
- Test scheduling stack overflow
- BLE scanning button protection

## [2.2] - 2026-04-14

### Added
- Complete microkernel architecture implementation
- Plugin-based test case management system
- Automated test case discovery and registration
- Comprehensive logging and reporting system

### Changed
- Migrated from old architecture to new microkernel design
- Restructured project directories and modules
- Updated all test cases to use new plugin system

### Fixed
- Architecture coupling issues
- Test case registration problems
- Module import and dependency management

## [2.1] - 2026-03-20

### Added
- Basic ADB communication framework
- Initial test case implementations
- Simple GUI interface with PyQt5

### Changed
- Improved device connection stability
- Enhanced error handling and user feedback

## [2.0] - 2026-02-15

### Added
- Complete rewrite with PyQt6
- Modular architecture design
- Comprehensive test suite for RV1126B devices

### Changed
- Migrated from PyQt5 to PyQt6
- Redesigned user interface
- Improved test execution engine

## [1.0] - 2026-01-01

### Added
- Initial release
- Basic ADB testing functionality
- Simple test case execution
- Basic reporting features

---

## Development Guidelines

### Version Numbering
We use [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 2.4.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

### Release Process
1. Update version in relevant files
2. Update CHANGELOG.md
3. Create git tag
4. Create GitHub release
5. Deploy to production if applicable