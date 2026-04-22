import os

def fix_test_case_imports():
    # 所有测试用例目录
    module_dirs = [
        'misc',
        'btwifi',
        'sdcard_firming',
        'multi_media',
        'stepper_motor_control',
        'tracking',
        'bleConfigureWifi',
        'ble_central',
        'http_agent',
        'mqtt_wrapper',
        'ota_update',
        'lvgl_app',
        'brushless_motor_control',
        'detect',
        'stream'
    ]
    
    fixed_count = 0
    
    for module_dir in module_dirs:
        if not os.path.exists(module_dir):
            continue
            
        # 递归查找所有test_*.py文件
        for root, dirs, files in os.walk(module_dir):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    print(f"Processing: {file_path}")
                    
                    try:
                        # 使用正确的编码读取
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否已经导入Module
                        if 'from commons import' in content and 'Module' in content:
                            print(f"  Already has Module import, skipping")
                            continue
                        
                        # 替换import行
                        if 'from commons import' in content:
                            # 查找导入行
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if line.startswith('from commons import'):
                                    if 'Module' not in line:
                                        lines[i] = line.rstrip() + ', Module'
                                        print(f"  Added Module import")
                                        fixed_count += 1
                                    break
                            
                            # 写回文件
                            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                                f.write('\n'.join(lines) + '\n')
                                
                    except Exception as e:
                        print(f"  Error: {e}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    fix_test_case_imports()