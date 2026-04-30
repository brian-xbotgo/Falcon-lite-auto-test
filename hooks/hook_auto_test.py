# PyInstaller 自动打包钩子：确保所有测试模块被打包进 exe
# 原理：读取 test_modules.txt 清单，将所有模块加入 hiddenimports
import os

def hook(hook_api):
    # 项目根目录（hooks 的父目录的父目录）
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 清单文件路径
    manifest_path = os.path.join(root_dir, 'test_modules.txt')
    
    # 尝试读取清单文件
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                test_modules = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        test_modules.append(line)
            
            hook_api.info(f"[hook_auto_test] 从清单加载 {len(test_modules)} 个测试模块")
            
            # 收集顶级包（确保顶级包也被打包）
            top_level_pkgs = set()
            for module in test_modules:
                top_pkg = module.split('.')[0]
                top_level_pkgs.add(top_pkg)
            
            # 合并：顶级包 + 所有测试模块
            all_imports = list(top_level_pkgs) + test_modules
            
            hook_api.add_imports(*all_imports)
            hook_api.info(f"[hook_auto_test] 添加 {len(all_imports)} 个导入（顶级包 {len(top_level_pkgs)} + 测试模块 {len(test_modules)}）")
        except Exception as e:
            hook_api.warning(f"[hook_auto_test] 读取清单失败: {e}，回退到扫描模式")
            _fallback_scan(hook_api, root_dir)
    else:
        hook_api.warning(f"[hook_auto_test] 清单文件未找到: {manifest_path}，使用扫描模式")
        _fallback_scan(hook_api, root_dir)


def _fallback_scan(hook_api, root_dir):
    """回退方案：扫描文件系统（开发环境）"""
    test_modules = []
    
    for root, dirs, files in os.walk(root_dir):
        # 跳过无关目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'venv', 'build', 'dist', 'node_modules']]
        
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                rel_path = os.path.relpath(root, root_dir)
                if rel_path == ".":
                    module_name = file[:-3]
                else:
                    module_name = f"{rel_path.replace(os.sep, '.')}.{file[:-3]}"
                test_modules.append(module_name)
    
    test_modules = list(set(test_modules))  # 去重
    hook_api.add_imports(*test_modules)
    hook_api.info(f"[hook_auto_test] 扫描模式：添加 {len(test_modules)} 个测试模块")
