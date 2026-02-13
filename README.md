# POE 自动喝药 / Buff 工具

适用于 Windows 平台的 POE 自动化辅助工具，支持：
- POE1：按键触发 / 计时触发的药水与 Buff 逻辑
- POE2：血蓝识别 + 阈值触发自动喝药

## 功能
- [x] 自动使用药水与立即技能，减少重复操作
- [x] 支持计时自动触发与按键触发
- [x] 支持多配置档（可按角色切换）
- [x] 仅在 POE 游戏窗口激活时触发
- [x] POE2 血蓝识别与自动喝药
- [ ] debuff 定向解状态（规划中）

## 环境需求
- Windows 10/11
- Python 3.10+（建议 3.12/3.13）

## 安装与运行（源码）

```powershell
pip install -r requirements.txt
python main.py
```

## 打包 EXE（推荐）
仓库已提供一键打包脚本。

### 方式 1：双击
- 运行 `build_exe.bat`

### 方式 2：命令行

```powershell
.\build_exe.bat
.\build_exe.bat -Name poe_AutoFlask_test
.\build_exe.bat -Console
```

默认会输出：
- `dist/poe_AutoFlask.exe`

## 使用说明
- 建议配置档按角色命名，方便切换
- `Del`：删除当前录入按键
- `Esc`：取消录入状态
- `Left Alt`：拖动悬浮窗
- 启动快捷键不支持鼠标键
- 药水/Buff 按键建议使用字母或数字键

## POE2 说明
- 在 `POE2` 页可配置：
  - 自动药水开关
  - 血瓶 / 蓝瓶按键
  - 血量 / 蓝量阈值
- 当前识别流程：
  - 基于游戏窗口区域截图
  - 固定左下/右下球体 ROI
  - 颜色识别并触发喝药

## 注意事项
- 请使用管理员权限启动程序，否则可能无法在游戏内正确触发按键
- 首次启动如果未生效，请重启程序后再试
- 每次启动后第一次建议鼠标点击一次“开始”按钮，之后可用快捷键切换
- 开始按钮为黄色通常表示当前不在游戏窗口，此时不会触发
- 游戏内打字可能触发按键，请注意聊天/交易场景
- 修改或切换配置前，建议先停止功能

## 项目结构
- `main.py`：程序入口与主窗口
- `ui/`：界面相关代码
- `utils/`：监听、识别、输入、配置、版本检查
- `configs/`：配置档 `.ini`
- `src/`：图标/图片资源
- `tools/`：调试与构建脚本
- `docs/`：功能说明与排障文档

## 相关文档
- `docs/POE2_SUPPORT_README.md`
- `docs/HEALTH_FEATURE_USAGE.md`
- `docs/FLASK_TRIGGER_LOGIC.md`
- `tools/README.md`

## 免责声明
本项目仅用于学习与技术研究，请自行评估并承担使用风险。
