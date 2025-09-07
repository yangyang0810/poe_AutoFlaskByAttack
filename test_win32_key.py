#!/usr/bin/env python3
"""
使用Windows API测试按键模拟
这是一个更底层的按键模拟方法
"""

import time
import win32api
import win32con
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

def send_key_vk(vk_code):
    """使用Windows API发送按键"""
    try:
        # 按下按键
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)  # 短暂延迟
        # 释放按键
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        print(f"发送按键失败: {e}")
        return False

def test_win32_keys():
    """测试Windows API按键模拟"""
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
    
    print("🎮 开始测试Windows API按键模拟...")
    print("请在5秒内切换到POE2游戏窗口，然后观察按键是否生效")
    
    for i in range(5, 0, -1):
        print(f"⏰ {i}秒后开始测试...")
        time.sleep(1)
    
    # 虚拟键码
    VK_1 = 0x31  # 数字1
    VK_2 = 0x32  # 数字2
    
    print("🚀 开始测试按键 '2' (Windows API)...")
    if send_key_vk(VK_2):
        print("✅ 按键 '2' 已发送")
    
    time.sleep(1)
    
    print("🚀 开始测试按键 '1' (Windows API)...")
    if send_key_vk(VK_1):
        print("✅ 按键 '1' 已发送")
    
    print("\n🎉 Windows API测试完成！")
    return True

if __name__ == "__main__":
    print("POE2 Windows API 按键模拟测试")
    print("=" * 50)
    test_win32_keys()
