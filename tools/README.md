# 工具脚本目录说明

- `install_pydirectinput.py`: 安装/检查输入模拟依赖。
- `test_key_press.py`: 使用 `pydirectinput` 的按键发送测试。
- `test_win32_key.py`: 使用 Win32 API 的按键发送测试。
- `debug_screenshots_test.py`: 分析 `debug_screenshots/` 截图并输出 `result.log`。

运行示例:

```powershell
python tools\debug_screenshots_test.py
python tools\test_key_press.py
python tools\test_win32_key.py
```
