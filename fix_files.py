import os

def fix_file_format():
    # 修复所有测试用例文件
    test_files = [
        r'misc\buzzer_test\test_buzzer_test.py',
        r'misc\led_check\test_led_flash.py',
        r'misc\power_test\test_power_up_down_test.py',
        r'misc\screen_test\test_screen_display.py',
        r'misc\version_info\test_version_read.py',
        r'btwifi\ble_wifi_test\test_client_connect_test.py',
        r'sdcard_firming\tf_card_check\test_tf_card_memory_check.py',
        r'multi_media\audio_test\test_audio_record_test.py',
        r'multi_media\camera_test\test_photo_record_test.py',
        r'multi_media\camera_test\test_video_record_test.py',
        r'stepper_motor_control\horizontal_motor_test\test_horizontal_motor_test.py',
        r'stepper_motor_control\pitch_motor_test\test_pitch_motor_test.py',
        r'tracking\track_test\test_auto_track_test.py',
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"Fixing: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 检查第一行导入是否包含Module
            for i, line in enumerate(lines):
                if line.startswith('from commons import'):
                    if 'Module' not in line:
                        lines[i] = line.rstrip() + ', Module\n'
                        print(f"  Added Module import")
                    break
            
            # 正确写入，保持换行符
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.writelines(lines)

if __name__ == '__main__':
    fix_file_format()