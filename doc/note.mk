# 该文件不允许自动写入，只允许人工维护

1.[P1][已完成]当前测试任务的参数：
class TestModel:
    """
    测试用例数据模型
    :param test_id: 测试用例唯一ID
    :param module: 测试模块
    :param name: 测试用例名称
    :param test_type: 测试类型（自动化（A）/人工（B））
    :param priority: 用例优先级（P0/P1/P2/P3/P4）
    :param status: 执行状态（等待中/执行中/通过/失败/待确认）
    :param duration: 执行耗时（单位：秒）
    :param remark: 测试备注/失败原因
    """
    # 测试用例ID
    test_id: str = ""
    # 归属模块
    module: Module = Module.MISC
    # 用例名称
    name: str = ""
    # 测试类型：自动化/人工
    test_type: str = "自动化"
    # 优先级：P0(最高)/P1/P2/...
    priority: Priority = Priority.P1
    # 执行状态
    status: str = "等待中"
    # 执行耗时（秒）
    duration: float = 0.0
    # 备注信息
    remark: str = ""

新需求：
	新增param:测试用例编号：初始化时可不填写，类型为字符串，生成的测试报告确认页面以及测试报告中都需要添加该列
	register中应该也要新增
	同时需要对目前已有的测试用例进行修复，测试用例编号暂不填写，需修改列表如下：
	`misc/version_info/test_version_read.py`
	`misc/led_check/test_led_flash.py`
	`misc/power_test/power_up_down_test.py`
	`misc/buzzer_test/buzzer_test.py`
	`misc/screen_test/screen_test.py`
	`misc/screen_test/test_wakeup_test.py`
	`misc/battery/test_battery_level_test.py`
	`misc/battery/test_battery_charge_status_test.py`
	`btwifi/ble_wifi_test/client_connect_test.py`
	`btwifi/ble_wifi_test/test_ble_display_test.py`
	`btwifi/ble_wifi_test/wifi_display_test.py`
	`sdcard_firming/tf_card_check/test_tf_card_memory_check.py`
	`multi_media/camera_test/video_record_test.py`
	`multi_media/camera_test/photo_record_test.py`
	`multi_media/audio_test/audio_record_test.py`
	`multi_media/camera_test/test_Mbtn_record_test.py`
	`multi_media/record_misc/test_scoreboard_watermark_test.py`
	`multi_media/live_streaming/test_live_streaming_test.py`
	`multi_media/record_misc/test_record_mark_test.py`
	`stepper_motor_control/horizontal_motor_test/horizontal_motor_test.py`
	`stepper_motor_control/pitch_motor_test/pitch_motor_test.py`
	`tracking/track_test/auto_track_test.py`

--------------------
2.[P2][已完成]修改测试用例：
	以下用例先前通过查找最新生成的文件并且配合时间检验存在bug，重新修改为在开始测试前先订阅ACR主题响应到一个通用的tmp中的txt文件中(相关内容请前往common中阅读了解一下)
	修改的测试用例包括：
		a.音频录制测试`multi_media/audio_test/test_audio_record_test.py`
		b.视频录制测试`multi_media/camera_test/test_video_record_test.py`
		c.拍照功能测试`multi_media/camera_test/test_photo_record_test.py`
	得到的输出内容示例：
		root@rk3576-buildroot:/tmp# cat test_mqtt_feedback.txt
		02026-05-06 16:21:56/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4
	判断方式：
		如果文件为空或内容格式不对则判断为失败
		如果文件内容格式正确且能够查到该文件则成功
	全面取消先前文件生成时间判断，完全按照新的流程
	1.  **视频录制测试**
    用例文件:  `multi_media/camera_test/test_video_record_test.py`
    描述:   1.检查/tmp/中是否有record_test工具与mp4info工具，没有则使用ADB推送  record_test与mp4info
                （注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
            2.执行录制流程：
                A.配置
                    执行命令:
                        mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C &
                        sleep 1
                        ./record_test mute 0
                        sleep 1
                    注：启动录音
                B.启动录制
                    执行命令:
                        ./record_test record 0 1 1 0
                        sleep 1
                    注：启动追踪
                C.Sleep 5
                D.结束录制
                    执行命令:
                        # 停止录制
                    ./record_test record 3 1 0 0
                E.获取到刚录制的文件的路径
                    执行命令:
                        cat "$OUTPUT_FILE"
                    得到的输出内容示例：
                        root@rk3576-buildroot:/tmp# cat test_mqtt_feedback.txt
                        02026-05-06 16:21:56/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4 
                    提取出文件路径:
                        /sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4
                    如果提取文件路径失败或根据该路径查找不到文件则判断为测试失败，跳过后续测试，添加测试备注以及日志，格式为：ACR订阅反馈：(cat返回的内容)
            3.执行文件检查流程:
                A.使用mp4info工具（根据设备使用不同版本）结合获取到的录制的文件路径
                    执行命令示例：./mp4info_rk3576 /.../VID*.mp4
                B.返回mp4info工具的输出
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
    优先级：P0
    状态: 启用

---
2.  **拍照功能测试**
    用例文件:  `multi_media/camera_test/test_photo_record_test.py`
    描述:   1.检查/tmp/中是否有record_test与IMG_check.sh工具，没有则使用ADB推送record_test与IMG_check.sh(工具都在tools中)
            2.执行拍摄命令:
                mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C &
                sleep 1
                ./record_test photo 2
                sleep 2
                获取到刚录制的文件的路径
                    执行命令:
                        cat "$OUTPUT_FILE"
                    得到的输出内容示例：
                        root@rk3576-buildroot:/tmp# cat test_mqtt_feedback.txt
                        02026-05-06 16:21:56/sdcard/falcon/20260506/IMG_20260506_162156_01_01.jpg
                    提取出文件路径:
                        /sdcard/falcon/20260506/IMG_20260506_162156_01_01.jpg
                    如果提取文件路径失败或根据该路径查找不到文件则判断为测试失败，跳过后续测试，添加测试备注以及日志，格式为：ACR订阅反馈：(cat返回的内容)
            3.使用IMG_check.sh工具进行判断
                执行命令:
                    ./IMG_check.sh 图片文件路径
                返回输出
            4.自动进行判断
                如果图片的格式为如下格式且status为normal则判定为通过，备注返回的内容
                    format:JPG(不固定)
                    status:normal
                    resolution:1920x1080（不固定）
                如果图片内容异常则status不为normal则判断为不通过，备注返回的内容

    支持设备: Falcon/Falcon-Air
    测试类型: 自动
    优先级：P1
    状态: 启用

---
3.  **音频录制测试**
    用例文件:  `multi_media/audio_test/test_audio_record_test.py`
    描述:   1.检查/tmp/中是否有record_test工具与mp4info工具，没有则使用ADB推送record_test与mp4info
                （注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
            2.执行录制流程：
                A.配置
                    执行命令:
                        mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C &
                        sleep 1
                        ./record_test mute 0
                        sleep 1
                    注：启动录音
                B.启动录制
                    执行命令:
                        ./record_test record 0 1 1 0
                        sleep 1
                    注：启动追踪
                C.Sleep 5
                D.结束录制
                    执行命令:
                        # 停止录制
                    ./record_test record 3 1 0 0
                E.获取到刚录制的文件的路径
                    执行命令:
                        cat "$OUTPUT_FILE"
                    得到的输出内容示例：
                        root@rk3576-buildroot:/tmp# cat test_mqtt_feedback.txt
                        02026-05-06 16:21:56/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4 
                    提取出文件路径:
                        /sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4
                    如果提取文件路径失败或根据该路径查找不到文件则判断为测试失败，跳过后续测试，添加测试备注以及日志，格式为：ACR订阅反馈：(cat返回的内容)
            3.执行文件检查流程:
                A.使用mp4info工具（根据设备使用不同版本）结合获取到的录制的文件路径
                    执行命令示例：./mp4info_rk3576 /.../VID*.mp4
                B.返回mp4info工具的输出
            4.进行自动判断检查
                mp4info工具输出格式:
                    info_rk3576 version -r
                    VID_20260422_105514_01_01.mp4:
                    Track   Type    Info
                    1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
                    2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
                    Encoded with: Lavf61.7.100
                A.如果输出内容正常且2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz这里的110kbps大于2则为通过测试
                    日志输出：audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz（示例）
                    测试备注：audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz（示例）
                B.如果输出内容异常，判断为测试不通过，备注：音频测试不通过；audio   MPEG-4 AAC LC, 9.450 secs, 2 kbps, 48000 Hz（示例）
    支持设备: Falcon/Falcon-Air
    测试类型: 自动
    优先级：P0
    状态: 启用
--------
4.  **M键录像测试**
    用例文件:  `multi_media/camera_test/test_Mbtn_record_test.py`
    描述:   1.检查/tmp/中是否有record_test工具与mp4info工具，没有则使用ADB推送record_test与mp4info
                （注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
            2.执行录制流程：
                A.启动录制
                    执行命令:
						mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C &
                        sleep 1
                        ./record_test record 0 2 0 0
						sleep 1
						./record_test record 0 1 0 0
                B.Sleep 3
                C.结束录制
                    执行命令:
                    	./record_test record 3 2 0 0
                D.获取到刚录制的文件的路径
                    E.获取到刚录制的文件的路径
						执行命令:
							cat "$OUTPUT_FILE"
						得到的输出内容示例：
							root@rk3576-buildroot:/tmp# cat test_mqtt_feedback.txt
							02026-05-06 16:21:56/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4 
						提取出文件路径:
							/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4
						如果提取文件路径失败或根据该路径查找不到文件则判断为测试失败，跳过后续测试，添加测试备注以及日志，格式为：ACR订阅反馈：(cat返回的内容)
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

--------------------
3.[P0][已完成]监听主题新增内容：
	当前多数需要监听MQTT主题的测试方式是将某个主题使用hexdump输出到一个bin文件中（示例：mosquitto_sub -h 127.0.0.1 -p 1883 -t 'ACR' -C 1 -W 60 | tee "TEST_MQTT_OUTPUT_FILE" | hexdump -C &），读取时使用的也是hexdump返回内容到本地进行解析

	新需求：经过分析发现有的主题返回的是字符串有的是十六进制内容，如果是字符串输出到txt中就不需要通过转换来分析，现在需要进行研究一下合理的修改方案能够兼容两种模式

--------------------
4.[P3]优化M键自动测试功能
	当前测试：通过record_test工具执行 ./record_test record 0 2 0 0和3 2 0 0
	中间需要间隔一分半进行测试
	
	修改为：	./record_test record 0 2 0 0	//进入预设录制倒计时	
				sleep 3
				./record_test record 0 1 0 0	//跳过倒计时启动录制
				sleep 5
				./record_test record 3 2 0 0	//结束录制
				修改后大幅度缩减测试时长

--------------------
5.[P4]报告类型新增：当前生成的报告为html格式，新增需求为同时生成 html和表格格式两种 两个文件内容保持一致

--------------------
6.[P3]新增测试用例
	1.自动追踪测试
		通过record_test工具执行M键预设进行录制（存在前提，设备的预设录制中的自动追踪不能被关闭）
		1.将record_test工具上传到tmp中
		2.监听ACR主题响应到一个txt文件(config,py中有设置路径且已封装好相关接口)
		3.执行./record_test record 0 2 0 0
			sleep 1
		4.执行./record_test record 0 1 0 0
			sleep 3
		5.执行./record_test record 3 2 0 0
			sleep 1
		6.cat txt文件得到:02026-05-06 16:21:56/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4(示例)
			提取出/sdcard/falcon/20260506/VID_20260506_162156_01_01.mp4路径
			修改路径为:/sdcard/falcon/20260506/.data/VID_20260506_162156_01_01.track
			如果追踪启动，track文件中的格式为：
				UTC2026-05-06 17:13:21.950
				Frame188 SZ0 Yaw0.50 Pit0.00 fps20.0
				AFilterP0 mot0 Deque0
				Fast0 Crowdx1280
				backCenterX1280
				FIN:x1280.0 V80.0 Yaw input0.0 output0.0 dir0 gear32
				Zoom:CPSz0 Count0
				
			通过以下命令进行文件判断：
				! grep -v -E '^$|^UTC[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}$|^Frame[0-9]+ SZ[0-9]+ Yaw[0-9.]+ Pit[0-9.]+ fps[0-9.]+$|^AFilterP[0-9]+ mot[0-9]+ Deque[0-9]+$|^Fast[0-9]+ Crowdx[0-9]+$|^backCenterX[0-9]+$|^FIN:x[0-9.]+ V[0-9.]+ Yaw input[0-9.]+ output[0-9.]+ dir[0-9]+ gear[0-9]+$|^Zoom:CPSz[0-9]+ Count[0-9]+$' "track文件路径" | grep -q . && echo "format error" || echo "format normal"
			如果输出format:normal则判断测试成功否则测试失败
			不论结果都将命令的返回加入到测试备注并且输出到日志

	2.记分牌自动测试
		1.检查当前记分牌状态:
			A.执行监听命令：mosquitto_sub -h 127.0.0.1 -p 1883 -t 'AUA' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C & (使用通用的bin文件地址)
			B.执行通知命令：mosquitto_pub -h 127.0.0.1 -p 1883 -t "AUR" -n
			C.得到监听结果:hexdump "$OUTPUT_FILE"
				得到的结果构造如下：
					root@rk3576-buildroot:/tmp# hexdump test_mqtt_feedback.bin
					0000000 0001 0000 0000 0000 0000 0000 0000 0000
					0000010 0000 0000 0000 0000 0000 0000 0000 0000
					*
					0000080 0100 0000 0000 0000 0000 0000 0000 0000
					0000090 0000 0000 0000 0000 0000 0000 0000 0000
					*
					0000190 0000 0000 0053 0094 0000 0a00
					000019c
				如果开头拆分后是0001则记分牌为关闭状态，进入下一步
				否则记分牌为启动状态，判定为测试成功，跳过后续设置
				如果跳过测试将hexdump的返回值加入到测试报告的备注中并且输出到日志，格式为：记分牌已处于启动状态
		2.启动记分牌并检验结果
			A.将预准备好的记分牌文件上传到tmp中
				文件在tools/bin_file/中，将open_scoreboard.bin和close_scoreboard.bin文件上传到tmp
			B.执行监听命令：mosquitto_sub -h 127.0.0.1 -p 1883 -t 'AUA' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C & ($OUTPUT_FILE使用通用的bin文件地址)
			C.执行设置命令：mosquitto_sub -h 127.0.0.1 -p 1883 -t "AWR" -f /tmp/open_scoreboard.bin
			D.执行通知命令：mosquitto_pub -h 127.0.0.1 -p 1883 -t "AUR" -n
			E.cat "$OUTPUT_FILE"如果内容包括：NBA Finals 2026 - Game 7 Live BroadcastLos Angeles LakersU%?bBoston Celtics圫S
				则判断测试成功
				否则判断测试失败
			F.不考虑结果，都执行关闭命令:mosquitto_sub -h 127.0.0.1 -p 1883 -t "AWR" -f /tmp/close_scoreboard.bin
				不考虑结果，都将cat得到的内容添加到备注中并且输出到日志，格式为：AUA订阅内容:（cat返回结果）

	3.电子围栏测试
		1.清空电子围栏
			执行：mosquitto_pub -p 1883 -t "CAR" -n && sleep 1
		2.准备
			执行：mosquitto_pub -p 1883 -t "CER" -n && sleep 1
		3.开始
			执行：mosquitto_pub -p 1883 -t "BYR" -n && sleep 1
		4.点位0:
			执行：printf '\x00\x00\x64\x00\x64' | mosquitto_pub -p 1883 -t "CBR" -s && sleep 1
		5.点位1:
			执行：printf '\x01\x01\xF4\x00\x64' | mosquitto_pub -p 1883 -t "CBR" -s && sleep 1
		6.点位2:
			执行：printf '\x02\x01\xF4\x01\x90' | mosquitto_pub -p 1883 -t "CBR" -s && sleep 1
		7.点位3:
			执行：printf '\x03\x00\x64\x01\x90' | mosquitto_pub -p 1883 -t "CBR" -s && sleep 1
		8.完成:
			执行：printf '\x00' | mosquitto_pub -p 1883 -t "BZR" -s && sleep 1
		9.查询结果:
			A.监听输出到文件
				执行：mosquitto_sub -h 127.0.0.1 -p 1883 -t 'CCA' -C 1 -W 60 | tee "$OUTPUT_FILE" | hexdump -C & ($OUTPUT_FILE使用通用的bin文件地址)
			B.sleep 1
			C.查询结果
				执行通知:mosquitto_pub -p 1883 -t "CCR" -n && sleep 1
				执行查询:hexdump "$OUTPUT_FILE"
					若输出的的内容为：
						root@rk3576-buildroot:/tmp# hexdump /tmp/test.bin
						0000000 0a01
						0000002
						则判断测试成功，添加测试备注并且输出到日志，格式为：CCR订阅内容:(hexdump返回内容)
					否则判断失败，添加测试备注并且输出到日志，格式为：CCR订阅内容:(hexdump返回内容)

	4.1080P30fps视频录制测试
		注：该测试项在原先的视频录制测试基础上修改
			1.检查/tmp/中是否有record_test工具、mp4info工具和set_1080P30fps.bin工具，没有则使用ADB推送record_test与mp4info
                （注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
            2.执行录制流程：
                A.配置
                    执行命令:
						mosquitto_pub -t "FHR" -f set_1080P30fps.bin && sleep 1
                        ./record_test mute 0
                        sleep 1
                    注：启动录音
                B.启动录制
                    执行命令:
                        ./record_test record 0 1 1 0
                        sleep 1
                    注：启动追踪
                C.Sleep 5
                D.结束录制
                    执行命令:
                        # 停止录制
                    ./record_test record 3 1 0 0
                E.获取到刚录制的文件的路径
                    执行命令:
                        ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 | head -1
            3.执行文件检查流程:
                A.使用mp4info工具（根据设备使用不同版本）结合获取到的录制的文件路径
                    执行命令示例：./mp4info_rk3576 /.../VID*.mp4
                B.返回mp4info工具的输出
            4.进行自动判断检查
                mp4info工具输出格式:
                    info_rk3576 version -r
                    VID_20260422_105514_01_01.mp4:
                    Track   Type    Info
                    1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
                    2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
                    Encoded with: Lavf61.7.100
                A.如果输出内容正常(格式正常且分辨率和帧率符合预期，帧率只要30开头)，则判断测试通过
                    日志输出：video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps（示例）
                    测试备注：video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps（示例）
                B.如果输出内容异常，判断为测试不通过，将输出的内容添加到测试备注并且输出到日志

	5.2K30fps视频录制测试
		注：该测试项在原先的视频录制测试基础上修改
			1.检查/tmp/中是否有record_test工具、mp4info工具和set_2K30fps.bin工具，没有则使用ADB推送record_test与mp4info
                （注：mp4info有两个版本，Falcon使用mp4info_rk3576，Falcon-Air使用mp4info_rv1126b）
            2.执行录制流程：
                A.配置
                    执行命令:
						mosquitto_pub -t "FHR" -f set_2K30fps.bin && sleep 1
                        ./record_test mute 0
                        sleep 1
                    注：启动录音
                B.启动录制
                    执行命令:
                        ./record_test record 0 1 1 0
                        sleep 1
                    注：启动追踪
                C.Sleep 5
                D.结束录制
                    执行命令:
                        # 停止录制
                    ./record_test record 3 1 0 0
                E.获取到刚录制的文件的路径
                    执行命令:
                        ls -t /sdcard/falcon/$(date +%Y%m%d)/*.mp4 | head -1
            3.执行文件检查流程:
                A.使用mp4info工具（根据设备使用不同版本）结合获取到的录制的文件路径
                    执行命令示例：./mp4info_rk3576 /.../VID*.mp4
                B.返回mp4info工具的输出
            4.进行自动判断检查
                mp4info工具输出格式:
                    info_rk3576 version -r
                    VID_20260422_105514_01_01.mp4:
                    Track   Type    Info
                    1       video   H264 High@4, 9.466 secs, 13225 kbps, 1920x1080 @ 30.107754 fps
                    2       audio   MPEG-4 AAC LC, 9.450 secs, 110 kbps, 48000 Hz
                    Encoded with: Lavf61.7.100
                A.如果输出内容正常(格式正常且分辨率和帧率符合预期,帧率只要30开头即可)，则判断测试通过
                    日志输出：video   H264 High@4, 9.466 secs, 13225 kbps, 2560x1440 @ 30.107754 fps（示例）
                    测试备注：video   H264 High@4, 9.466 secs, 13225 kbps, 2560x1440 @ 30.107754 fps（示例）
                B.如果输出内容异常，判断为测试不通过，将输出的内容添加到测试备注并且输出到日志
	



	
