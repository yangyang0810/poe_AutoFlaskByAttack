# 项目文件夹分析与整改状态

## 1. 项目定位
- 类型: Windows 平台 Python + PyQt5 桌面工具
- 入口: `main.py`
- 目标功能: POE1/POE2 自动喝药、血蓝监控、悬浮窗控制

## 2. 现有目录结构（整改后）
- `main.py`: 主窗口与主流程
- `configs.py`: 默认配置模板
- `configs/`: 多配置档 `.ini`
- `ui/`: UI 界面与自定义控件
- `utils/`: 输入监听、窗口检测、监控、配置与版本检查
- `src/`: 图标和内嵌图片资源
- `docs/`: 项目文档与排障记录
- `tools/`: 调试/验证脚本
- `debug_screenshots/`: 调试截图样本目录

## 3. 已完成整改
- 目录重组:
  - 已将说明文档迁移到 `docs/`
  - 已将调试脚本迁移到 `tools/`
- 命名修复:
  - `utils/check_versoin.py` 已重命名为 `utils/check_version.py`
  - `main.py` 导入路径已同步更新
- 路径修复:
  - `tools/debug_screenshots_test.py` 已修正为从项目根目录定位 `debug_screenshots/`
- 仓库清洁:
  - `.gitignore` 已忽略 `log/`、`debug_*.png`、`debug_screenshots/result.log`

## 4. 仍建议继续优化
- 统一文本编码为 UTF-8（README/UI 文案存在乱码风险）
- 统一模块命名风格（如 `ui/A.py` 可改为语义化文件名）
- 为 `tools/` 脚本补充最小参数说明和失败排障提示
- 在 `README.md` 增加目录结构与开发调试章节
