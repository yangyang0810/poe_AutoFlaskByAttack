#!/usr/bin/env python3
"""
安装 pydirectinput 库的脚本
运行此脚本来安装 pydirectinput 库
"""

import subprocess
import sys

def install_pydirectinput():
    """安装 pydirectinput 库"""
    try:
        print("正在安装 pydirectinput 库...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydirectinput"])
        print("✅ pydirectinput 安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

if __name__ == "__main__":
    print("POE2 自动药水 - 安装 pydirectinput 库")
    print("=" * 50)
    
    if install_pydirectinput():
        print("\n🎉 安装完成！现在可以运行程序了。")
        print("如果游戏内仍然没有反应，请尝试以管理员权限运行程序。")
    else:
        print("\n💡 如果安装失败，请手动运行以下命令：")
        print("pip install pydirectinput")
