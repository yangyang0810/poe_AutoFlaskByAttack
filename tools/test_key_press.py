#!/usr/bin/env python3
"""
测试按键模拟脚本
用于验证 pydirectinput 是否能在POE2中正常工作
"""

import time
import pydirectinput
import win32gui

def find_poe2_window():
    """查找POE2游戏窗口"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if "Path of Exile 2" in window_title:
                windows.append((hwnd, window_title))
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

def test_key_press():
    """测试按键模拟"""
    print("🔍 查找POE2游戏窗口...")
    poe2_windows = find_poe2_window()
    
    if not poe2_windows:
        print("❌ 未找到POE2游戏窗口，请确保游戏正在运行")
        return False
    
    print(f"✅ 找到POE2窗口: {poe2_windows[0][1]}")
    
    # 切换到POE2窗口
    hwnd = poe2_windows[0][0]
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    
    print("🎮 开始测试按键模拟...")
    print("请在5秒内切换到POE2游戏窗口，然后观察按键是否生效")
    
    for i in range(5, 0, -1):
        print(f"⏰ {i}秒后开始测试...")
        time.sleep(1)
    
    print("🚀 开始测试按键 '2'...")
    
    try:
        # 测试按键2
        pydirectinput.press('2')
        print("✅ 按键 '2' 已发送")
        
        time.sleep(1)
        
        # 测试按键1
        print("🚀 开始测试按键 '1'...")
        pydirectinput.press('1')
        print("✅ 按键 '1' 已发送")
        
        print("\n🎉 测试完成！")
        print("如果游戏内没有反应，可能的原因：")
        print("1. 游戏有防作弊保护")
        print("2. 需要管理员权限")
        print("3. 按键绑定不正确")
        print("4. 游戏窗口没有正确获得焦点")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("POE2 按键模拟测试")
    print("=" * 50)
    test_key_press()
