# -*- coding: utf-8 -*-
"""
Health Configuration Widget for POE Auto Flask
Simple UI extension for health-based flask configuration
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class HealthConfigWidget(QtWidgets.QGroupBox):
    """Widget for configuring health-based flask settings"""
    
    def __init__(self, parent, title="血量药水设置"):
        super().__init__(title, parent)
        self.parent_main = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the health configuration UI"""
        self.setFont(QtGui.QFont('微軟正黑體', 10))
        self.setGeometry(QtCore.QRect(30, 400, 450, 200))
        self.setStyleSheet("""
            QGroupBox {
                color: #E6E6E6;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Health monitoring enable checkbox
        self.cb_health_monitor = QtWidgets.QCheckBox("启用血量监控", self)
        self.cb_health_monitor.setGeometry(QtCore.QRect(10, 25, 120, 20))
        self.cb_health_monitor.setFont(QtGui.QFont('微軟正黑體', 9))
        self.cb_health_monitor.setStyleSheet("color: #E6E6E6;")
        self.cb_health_monitor.setChecked(True)
        
        # Health threshold label and slider
        self.label_health_threshold = QtWidgets.QLabel("血量阈值: 30%", self)
        self.label_health_threshold.setGeometry(QtCore.QRect(150, 25, 100, 20))
        self.label_health_threshold.setFont(QtGui.QFont('微軟正黑體', 9))
        self.label_health_threshold.setStyleSheet("color: #E6E6E6;")
        
        self.slider_health_threshold = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider_health_threshold.setGeometry(QtCore.QRect(260, 25, 150, 20))
        self.slider_health_threshold.setRange(10, 80)
        self.slider_health_threshold.setValue(30)
        self.slider_health_threshold.valueChanged.connect(self.on_health_threshold_changed)
        
        # Health flask configuration
        y_offset = 55
        
        # Headers
        headers = ["按键", "冷却时间", "血量阈值%"]
        x_positions = [10, 80, 150]
        for i, header in enumerate(headers):
            label = QtWidgets.QLabel(header, self)
            label.setGeometry(QtCore.QRect(x_positions[i], y_offset, 60, 20))
            label.setFont(QtGui.QFont('微軟正黑體', 9))
            label.setStyleSheet("color: #E6E6E6;")
        
        # Health flasks (3 slots)
        self.health_flask_keys = []
        self.health_flask_times = []
        self.health_flask_thresholds = []
        
        for i in range(3):
            y = y_offset + 25 + i * 30
            
            # Flask key input
            key_edit = QtWidgets.QLineEdit(self)
            key_edit.setGeometry(QtCore.QRect(10, y, 50, 25))
            key_edit.setAlignment(Qt.AlignCenter)
            key_edit.setMaxLength(1)
            key_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #000000;
                    color: #E6E6E6;
                    border: 1px solid #555;
                }
            """)
            self.health_flask_keys.append(key_edit)
            
            # Flask cooldown time
            time_edit = QtWidgets.QLineEdit(self)
            time_edit.setGeometry(QtCore.QRect(80, y, 50, 25))
            time_edit.setAlignment(Qt.AlignCenter)
            time_edit.setPlaceholderText("5.0")
            time_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #000000;
                    color: #E6E6E6;
                    border: 1px solid #555;
                }
            """)
            self.health_flask_times.append(time_edit)
            
            # Health threshold
            threshold_edit = QtWidgets.QLineEdit(self)
            threshold_edit.setGeometry(QtCore.QRect(150, y, 50, 25))
            threshold_edit.setAlignment(Qt.AlignCenter)
            threshold_edit.setPlaceholderText("30")
            threshold_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #000000;
                    color: #E6E6E6;
                    border: 1px solid #555;
                }
            """)
            self.health_flask_thresholds.append(threshold_edit)
        
        # Emergency flask section
        emergency_label = QtWidgets.QLabel("紧急药水 (15%血量触发):", self)
        emergency_label.setGeometry(QtCore.QRect(230, y_offset, 150, 20))
        emergency_label.setFont(QtGui.QFont('微軟正黑體', 9))
        emergency_label.setStyleSheet("color: #FF6666;")
        
        # Emergency flask inputs
        self.emergency_flask_keys = []
        self.emergency_flask_times = []
        
        for i in range(2):
            y = y_offset + 25 + i * 30
            
            # Emergency key
            key_edit = QtWidgets.QLineEdit(self)
            key_edit.setGeometry(QtCore.QRect(230, y, 50, 25))
            key_edit.setAlignment(Qt.AlignCenter)
            key_edit.setMaxLength(1)
            key_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #200000;
                    color: #FF6666;
                    border: 1px solid #FF6666;
                }
            """)
            self.emergency_flask_keys.append(key_edit)
            
            # Emergency time
            time_edit = QtWidgets.QLineEdit(self)
            time_edit.setGeometry(QtCore.QRect(290, y, 50, 25))
            time_edit.setAlignment(Qt.AlignCenter)
            time_edit.setPlaceholderText("3.0")
            time_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #200000;
                    color: #FF6666;
                    border: 1px solid #FF6666;
                }
            """)
            self.emergency_flask_times.append(time_edit)
        
        # Calibration button for health bar position
        self.btn_calibrate = QtWidgets.QPushButton("校准血条位置", self)
        self.btn_calibrate.setGeometry(QtCore.QRect(350, 25, 90, 25))
        self.btn_calibrate.setFont(QtGui.QFont('微軟正黑體', 9))
        self.btn_calibrate.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #E6E6E6;
                border: 1px solid #666;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.btn_calibrate.clicked.connect(self.calibrate_health_bar)
        
        # Status label
        self.label_status = QtWidgets.QLabel("状态: 未启用", self)
        self.label_status.setGeometry(QtCore.QRect(350, 55, 90, 20))
        self.label_status.setFont(QtGui.QFont('微軟正黑體', 8))
        self.label_status.setStyleSheet("color: #CCCCCC;")
    
    def on_health_threshold_changed(self, value):
        """Handle health threshold slider change"""
        self.label_health_threshold.setText(f"血量阈值: {value}%")
        
        # Update all threshold inputs to this value if they're empty
        for threshold_edit in self.health_flask_thresholds:
            if threshold_edit.text() == "":
                threshold_edit.setText(str(value))
    
    def calibrate_health_bar(self):
        """Open calibration dialog for health bar position"""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("血条校准")
        msg.setText("请确保POE游戏窗口可见，然后点击确定开始校准血条位置。\n\n"
                   "校准过程中程序会截取屏幕并尝试自动识别血条位置。\n"
                   "如果自动识别失败，您可能需要手动调整血条区域坐标。")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        
        if msg.exec_() == QtWidgets.QMessageBox.Ok:
            # Here you would implement the calibration logic
            self.label_status.setText("状态: 校准中...")
            self.label_status.setStyleSheet("color: #FFAA00;")
            
            # Simulate calibration (in real implementation, this would do actual calibration)
            QtCore.QTimer.singleShot(2000, self.calibration_complete)
    
    def calibration_complete(self):
        """Handle calibration completion"""
        self.label_status.setText("状态: 已校准")
        self.label_status.setStyleSheet("color: #66FF66;")
    
    def get_health_config(self):
        """Get current health configuration"""
        config = {
            'enabled': self.cb_health_monitor.isChecked(),
            'default_threshold': self.slider_health_threshold.value(),
            'health_flasks': [],
            'emergency_flasks': []
        }
        
        # Get health flask settings
        for i in range(3):
            key = self.health_flask_keys[i].text().strip()
            time_text = self.health_flask_times[i].text().strip()
            threshold_text = self.health_flask_thresholds[i].text().strip()
            
            if key and time_text:
                try:
                    cooldown = float(time_text)
                    threshold = int(threshold_text) if threshold_text else 30
                    config['health_flasks'].append({
                        'key': key,
                        'cooldown': cooldown,
                        'threshold': threshold
                    })
                except ValueError:
                    continue
        
        # Get emergency flask settings
        for i in range(2):
            key = self.emergency_flask_keys[i].text().strip()
            time_text = self.emergency_flask_times[i].text().strip()
            
            if key and time_text:
                try:
                    cooldown = float(time_text)
                    config['emergency_flasks'].append({
                        'key': key,
                        'cooldown': cooldown
                    })
                except ValueError:
                    continue
        
        return config
    
    def load_health_config(self, config):
        """Load health configuration from settings"""
        if 'enabled' in config:
            self.cb_health_monitor.setChecked(config['enabled'])
        
        if 'default_threshold' in config:
            self.slider_health_threshold.setValue(config['default_threshold'])
            self.on_health_threshold_changed(config['default_threshold'])
        
        # Load health flask settings
        health_flasks = config.get('health_flasks', [])
        for i, flask in enumerate(health_flasks[:3]):
            if i < len(self.health_flask_keys):
                self.health_flask_keys[i].setText(flask.get('key', ''))
                self.health_flask_times[i].setText(str(flask.get('cooldown', '')))
                self.health_flask_thresholds[i].setText(str(flask.get('threshold', '')))
        
        # Load emergency flask settings
        emergency_flasks = config.get('emergency_flasks', [])
        for i, flask in enumerate(emergency_flasks[:2]):
            if i < len(self.emergency_flask_keys):
                self.emergency_flask_keys[i].setText(flask.get('key', ''))
                self.emergency_flask_times[i].setText(str(flask.get('cooldown', '')))
