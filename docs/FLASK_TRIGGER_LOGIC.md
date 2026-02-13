# POE自动喝药水 - 触发按钮逻辑说明

## 🔧 触发按钮逻辑位置

### 1. 主要触发逻辑
**文件**: `utils/input_listener.py`
**方法**: `on_flask_trigger(self, flask_type)`

这是主要的触发按钮逻辑，当健康监控器检测到血量和蓝量变化时会调用此方法。

### 2. 触发信号发送
**文件**: `utils/health_monitor.py`
**方法**: `update_health_mana()` 中的 `self.flask_trigger.emit()`

健康监控器在检测到血量和蓝量低于阈值时会发送触发信号。

### 3. 信号连接
**文件**: `main.py` 和 `utils/input_listener.py`
**连接**: `self.health_monitor.flask_trigger.connect(self.on_flask_trigger)`

将健康监控器的信号连接到触发处理方法。

## ⚙️ 触发逻辑流程

```
1. 健康监控器检测血量和蓝量
   ↓
2. 如果血量/蓝量低于阈值，发送 flask_trigger 信号
   ↓
3. input_listener 接收信号，调用 on_flask_trigger 方法
   ↓
4. 检查冷却时间，如果允许则触发按键
   ↓
5. 调用 simulate_key_press 模拟按键
```

## 🕐 冷却时间设置

### 当前设置
- **血量药水**: 1秒冷却时间
- **蓝量药水**: 5秒冷却时间

### 配置选项
```ini
[poe2_auto_flask]
health_flask_cooldown=1.0  # 血量药水冷却时间(秒)
mana_flask_cooldown=5.0    # 蓝量药水冷却时间(秒)
```

## 🔍 触发条件

### 血量药水触发
- 血量低于设定阈值 (默认75%)
- 距离上次触发超过冷却时间 (默认1秒)

### 蓝量药水触发
- 蓝量低于设定阈值 (默认55%)
- 距离上次触发超过冷却时间 (默认5秒)

## 📝 调试信息

程序会在控制台输出以下信息：
- `Auto triggered health flask: 1` - 触发血量药水
- `Auto triggered mana flask: 2` - 触发蓝量药水
- `Mana flask on cooldown, X.Xs remaining` - 蓝药冷却中

## 🛠️ 修改冷却时间

### 方法1: 修改配置文件
编辑 `configs/poe2_test.ini` 或当前使用的配置文件：
```ini
[poe2_auto_flask]
mana_flask_cooldown=5.0  # 改为你想要的秒数
```

### 方法2: 修改代码默认值
在 `utils/input_listener.py` 中修改：
```python
self.mana_flask_cooldown = 5.0    # 改为你想要的秒数
```

## ⚠️ 注意事项

1. **冷却时间过短**: 可能导致药水使用过于频繁
2. **冷却时间过长**: 可能导致血量/蓝量过低时无法及时补充
3. **建议设置**: 血量药水1-2秒，蓝量药水3-5秒

## 🔧 故障排除

如果触发按钮不工作：

1. **检查配置**: 确认 `poe2_auto_flask.enabled=True`
2. **检查阈值**: 确认血量和蓝量阈值设置合理
3. **检查冷却**: 确认冷却时间设置正确
4. **查看日志**: 检查控制台输出的调试信息
5. **测试按键**: 手动按1和2键确认药水能正常使用
