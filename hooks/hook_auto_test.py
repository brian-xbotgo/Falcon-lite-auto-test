# PyInstaller自动打包钩子：自动扫描所有test_*测试模块，强制打包进exe
import os
import glob

def hook(hook_api):
    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_modules = []

    # 递归扫描所有test_*.py文件，转换为模块名
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                # 计算模块名
                rel_path = os.path.relpath(root, root_dir)
                if rel_path == ".":
                    module_name = file[:-3]
                else:
                    module_name = f"{rel_path.replace(os.sep, '.')}.{file[:-3]}"
                test_modules.append(module_name)
    
    # 强制添加到隐藏导入，让PyInstaller打包所有测试模块
    hook_api.add_imports(*test_modules)