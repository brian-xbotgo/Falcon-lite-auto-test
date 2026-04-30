#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证清单文件正确性
检查 test_modules.txt 中的所有模块是否可导入
"""

import sys
import importlib

def check_manifest():
    manifest_path = 'test_modules.txt'
    
    print("=" * 60)
    print("测试模块清单验证")
    print("=" * 60)
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            modules = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ 清单文件不存在: {manifest_path}")
        return False
    
    print(f"清单包含 {len(modules)} 个模块\n")
    
    # 预先导入 commons（这些模块需要 commons 包）
    try:
        import commons
        print("✅ 导入 commons 成功")
    except ImportError as e:
        print(f"❌ 导入 commons 失败: {e}")
        return False
    
    # 尝试导入每个模块
    failed = []
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: {type(e).__name__}: {e}")
            failed.append(module_name)
    
    print("\n" + "=" * 60)
    if failed:
        print(f"❌ 有 {len(failed)} 个模块导入失败")
        print("失败的模块：")
        for m in failed:
            print(f"  - {m}")
        return False
    else:
        print(f"✅ 所有 {len(modules)} 个模块导入成功")
        return True

if __name__ == '__main__':
    success = check_manifest()
    sys.exit(0 if success else 1)
