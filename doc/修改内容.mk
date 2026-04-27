# 测试用例修改记录
**版本：V2.4（2026-04-27 测试用例优化版）**

## 最新修改内容 (2026-04-27)

### 1. M键录像测试自动化实现
**修改文件**：`multi_media/camera_test/test_Mbtn_record_test.py`
**修改类型**：人工测试 → 自动化测试
**修改内容**：
- 改为自动化测试（测试ID：A）
- 实现完整的90秒录制流程：`record 0 2 0 0` → 录制90秒 → `record 3 2 0 0`
- 添加文件时间合理性验证
- 集成mp4info工具自动验证录制文件完整性
- 支持Falcon/Falcon-Air设备类型自动检测

### 2. 睡眠唤醒测试MQTT集成
**修改文件**：`misc/screen_test/test_wakeup_test.py`
**修改类型**：功能增强
**修改内容**：
- 添加MQTT命令发送：`printf '\x01' | mosquitto_pub -h localhost -t "FSR" -s`
- 使用原始字符串(r前缀)避免转义问题
- 保持人工观察确认的测试类型

### 3. 录制打点测试新增
**新增文件**：`multi_media/record_misc/test_record_mark_test.py`
**新增类型**：全新自动化测试用例
**功能描述**：
- 实现录制打点完整流程：`record 0 1 0 0` → 5秒 → `mark` → 5秒 → `record 3 1 0 0`
- 检查文件生成时间不超过1分半钟
- 验证对应的mark文件是否存在于`.data`文件夹
- 支持Falcon/Falcon-Air设备类型

## ------------------------------------------------

## 历史修改内容

新测试方案分析：

1.在tmp中维护一个同文件，将订阅的MQTT主题内容输出到这个文件中
2.封装通用将订阅主题输出到文件中与文件清空函数，设置统一文件路径与文件名
3.运行到测试用例时，首先实现MQTT监听订阅到文件中，然后发送MQTT指令，等待n秒，读取文件结果，根据文件结果来判断测试用例是否通过

通过adb依次发送命令
订阅与发送示例：
a.统一设定地址
OUTPUT_FILE="/tmp/test_feedback.bin"
b.发送订阅依次命令
mosquitto_sub -h 127.0.0.1 -p 1883 -t 'CSA' -C 1 -W 60 | tee "/tmp/test_feedback.bin" | hexdump -C &
c.获取进程ID
SUB_PID=$!
sleep 0.2
d.发送消息命令
mosquitto_pub -h 127.0.0.1 -p 1883 -t 'CSR' -n
e.等待进程
wait $SUB_PID

f.读取文件时采用hexdump读取文件


# ------------------------------------------------
测试用例分析：
阅读doc中的架构规范、上位机项目架构和增减测试用例教程，接着阅读common文件夹中的底层代码，接着阅读multi_medi/camera_test/test_video_record_test.py，我需要你帮我做几个测试用例内容的修改以及新增一个测试用例，内容如下
修改测试用例：
---
4.  **M键录像测试**
用例文件:  `multi_media/camera_test/test_Mbtn_record_test.py`
描述:   1.检查/tmp/中是否有record_test工具与mp4info工具，没有则使用ADB推送record_test与mp4info
（注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
2.执行录制流程：
A.启动录制
	执行命令:
		./record_test record 0 2 0 0
B.Sleep 90秒
C.结束录制
	执行命令:
		./record_test record 3 2 0 0
D.获取到刚录制的文件的路径
	执行命令:
		ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 | head -1
3.执行文件检查流程:
A.检查文件生成的时间是否合理以此来判断是否新生成的文件
B.使用mp4info工具（根据设备使用不同版本）结合获取到的录制的文件路径
	执行命令示例：./mp4info_rk3576 /.../VID*.mp4
C.返回mp4info工具的输出
4.进行自动判断检查
mp4info工具输出格式:
	info_rk3576 version -r
	VID_20260422_105514_01_01.mp4:
	Track   Type    Info
	1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
	2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
	Encoded with: Lavf61.7.100
A.如果输出内容正常，则判断测试通过
	日志输出：video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps（示例）
	测试备注：video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps（示例）
B.如果输出内容异常，判断为测试不通过，将输出的内容添加到测试备注并且输出到日志
支持设备: Falcon/Falcon-Air
测试类型: 自动
优先级：P1
状态: 启用
备注：参考视频录制测试

---
6.  **睡眠唤醒测试**
用例文件: `misc/screen_test/test_wakeup_test.py`
描述:   1.发送ADB命令：printf '\x01' | mosquitto_pub -h localhost -t "FSR" -s
2.通知人工观察设备屏幕是否唤醒，侧灯是否闪烁
支持设备: Falcon/Falcon-Air
测试类型: 人工
优先级：P2
状态: 启用


新增测试用例：
7.  **录制打点测试**
用例文件:  `multi_media/record_misc/test_record_mark_test.py`
描述:   1.检查/tmp/中是否有record_test工具与mp4info工具，没有则使用ADB推送record_test与mp4info
（注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
2.执行录制流程：
A.启动录制
	执行命令:
		./record_test record 0 1 0 0
B.sleep 5
C.执行打点
	执行命令:
		./record_test mark
D.sleep 5
E.结束录制
	执行命令:
		./record_test record 3 1 0 0
F.获取到刚录制的文件的路径
	执行命令:
		ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 | head -1
		ls得到的文件路径格式为：/sdcard/falcon/20260427/VID_20260427_104957_01_01.mp4（示例）
3.执行文件检查流程并进行判断:
A.检查文件生成的时间是否合理以此来判断是否新生成的文件，如果文件生成的时间超过一分半钟，则直接判断为测试失败
	备注：生成文件超出时间限制：/sdcard/falcon/20260427/VID_20260427_104957_01_01.mp4（示例）
B.查找对应的打点文件
	需要查询文件路径下.data文件夹是否存在对应的mark文件
		/sdcard/falcon/20260427/.data/VID_20260427_104957_01_01.mark（示例）
	如果存在mark文件则测试通过，返回/sdcard/falcon/20260427/.data/VID_20260427_104957_01_01.mark
		备注：打点文件成功生成：/sdcard/falcon/20260427/.data/VID_20260427_104957_01_01.mark
	如果不存在mark文件则测试不通过
支持设备: Falcon/Falcon-Air
测试类型: 自动化
优先级：P2
状态: 启用
备注：参考视频录制测试
