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
自动化测试方案分析：

1.音频查询方式：
	使用record_test工具设置启动音频录制，录制一段视频
	使用mp4info工具对视频进行解析
	执行得到内容：如果audio读到2kbps则为静音，如果大于则为音频录制正常
	info_rk3576 version -r
	VID_20260422_105514_01_01.mp4:
	Track   Type    Info
	1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
	2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
	Encoded with: Lavf61.7.100

2.视频录制检查：
	使用record_test工具录制一段视频
	使用mp4info工具对视频进行解析
	执行得到内容：如果audio读到2kbps则为静音，如果大于则为音频录制正常
	info_rk3576 version -r
	VID_20260422_105514_01_01.mp4:
	Track   Type    Info
	1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
	2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
	Encoded with: Lavf61.7.100

3.追踪查询方式：录制结束后需要得到录制的文件名称
	如果hexdump .data/VID*.track文件
		文件不存在
		NULL
		0000000 6552 6573 5374 4b44 0a0a
		000000a
	则追踪未启动

4.电机测试优化:
	mosquitto_sub -h 127.0.0.1 -t BXA -C 1 -W 5 > 公用的bin文件 &
	mosquitto_pub -h 127.0.0.1 -t BXR -n
	读取一次文件，拿到一次角度
	清空bin文件
	mosquitto_sub -h 127.0.0.1 -t BXA -C 1 -W 5 > 公用的bin文件 &
	mosquitto_pub -h 127.0.0.1 -t BXR -n
	再次读取文件
	对比两次角度是否有差异，若有差异自动判断电机运行成功

5.拍照功能测试:
	通过record_test photo拍摄照片
	得到拍摄的图片路径与名称
	使用写好的图片检测脚本IMG_check.sh分析图片
	根据IMG_check.sh的结果进行判断


新任务：测试用例 shell 脚本化


# -------------------------------------------------



