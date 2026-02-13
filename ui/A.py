# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QTabWidget, QWidget, QCheckBox

from ui.my_widgets import *
from src.logo_png import logo_png
from src.flask_png import flask_png
from utils.utils import display_image, now_version


class A_form:
    def __init__(self, Form, event):
        self.main = Form
        Form.setObjectName("MainWindow")
        Form.resize(511, 800)
        Form.setMinimumSize(QtCore.QSize(511, 800))
        Form.setMaximumSize(QtCore.QSize(511, 800))
        Form.setStyleSheet('QMainWindow {background-color: #242424; color: #E6E6E6;}')

        self.font36 = QtGui.QFont('Microsoft JhengHei', 36)
        self.font16 = QtGui.QFont('Microsoft JhengHei', 16)
        self.font12 = QtGui.QFont('Microsoft JhengHei', 12)
        self.font9 = QtGui.QFont('Microsoft JhengHei', 9)

        self.label_main = flask_label(Form, event)
        self.label_main.setGeometry(QtCore.QRect(30, 30, 215, 94))
        display_image(self.label_main, flask_png)

        self.label_ver = my_label(Form)
        self.label_ver.setGeometry(QtCore.QRect(10, 5, 150, 20))
        self.label_ver.setFont(self.font9)

        self.label_logo = clickable_label(Form, event)
        self.label_logo.setGeometry(QtCore.QRect(440, 10, 60, 60))
        display_image(self.label_logo, logo_png)

        self.btn_start = my_btn(Form)
        self.btn_start.setFont(self.font12)
        self.btn_start.setGeometry(QtCore.QRect(390, 90, 91, 31))

        self.gb_global = my_gb(Form)
        self.gb_global.setFont(self.font12)
        self.gb_global.setGeometry(QtCore.QRect(260, 30, 121, 94))

        self.edit_global_enable_key = focus_line_edit(self.gb_global, event, 'global', 0)
        self.edit_global_enable_key.setFont(self.font12)
        self.edit_global_enable_key.setGeometry(QtCore.QRect(10, 30, 101, 51))
        self.edit_global_enable_key.setAlignment(Qt.AlignCenter)
        self.edit_global_enable_key.setReadOnly(True)

        self.sets_index_labels = []
        for i in range(5):
            _label = my_label(Form)
            _label.setGeometry(QtCore.QRect(54 + 38 * i, 120, 20, 20))
            _label.setFont(self.font9)
            _label.setText("")
            self.sets_index_labels.append(_label)

        self.edit_new_config = my_line_edit(Form)
        self.edit_new_config.setFont(self.font12)
        self.edit_new_config.setGeometry(QtCore.QRect(30, 140, 251, 31))
        self.edit_new_config.setAlignment(Qt.AlignCenter)

        self.btn_new_config = my_btn(Form)
        self.btn_new_config.setFont(self.font12)
        self.btn_new_config.setGeometry(QtCore.QRect(290, 140, 91, 31))

        self.btn_rename_config = my_btn(Form)
        self.btn_rename_config.setFont(self.font12)
        self.btn_rename_config.setGeometry(QtCore.QRect(390, 140, 91, 31))

        self.combo_config = my_ComboBox(Form)
        self.combo_config.setFont(self.font12)
        self.combo_config.setGeometry(QtCore.QRect(30, 180, 351, 31))
        self.combo_config.setEditable(True)
        self.combo_config.lineEdit().setFont(self.font12)
        self.combo_config.lineEdit().setReadOnly(True)
        self.combo_config.lineEdit().setAlignment(Qt.AlignCenter)

        self.btn_save_config = my_btn(Form)
        self.btn_save_config.setFont(self.font12)
        self.btn_save_config.setGeometry(QtCore.QRect(390, 180, 91, 31))

        self.tab_widget = QTabWidget(Form)
        self.tab_widget.setFont(self.font12)
        self.tab_widget.setGeometry(QtCore.QRect(20, 220, 471, 520))

        self.tab_poe1 = QWidget()
        self.tab_poe1.setObjectName("tab_poe1")
        self.tab_widget.addTab(self.tab_poe1, "POE1")

        self.tab_poe2 = QWidget()
        self.tab_poe2.setObjectName("tab_poe2")
        self.tab_widget.addTab(self.tab_poe2, "POE2")

        self.btn_del_config = my_btn(Form)
        self.btn_del_config.setFont(self.font12)
        self.btn_del_config.setGeometry(QtCore.QRect(390, 760, 91, 31))

        self.btn_floating_win = my_btn(Form)
        self.btn_floating_win.setFont(self.font12)
        self.btn_floating_win.setGeometry(QtCore.QRect(30, 760, 91, 31))

        # POE1 tab
        self.gb_flask = my_gb(self.tab_poe1)
        self.gb_flask.setFont(self.font12)
        self.gb_flask.setGeometry(QtCore.QRect(20, 10, 431, 161))

        self.edit_flask_key = []
        for i in range(5):
            _edit = focus_line_edit(self.gb_flask, event, 'flask', i)
            _edit.setFont(self.font36)
            _edit.setGeometry(QtCore.QRect(30 + 80 * i, 30, 51, 71))
            _edit.setAlignment(Qt.AlignCenter)
            _edit.setReadOnly(True)
            self.edit_flask_key.append(_edit)

        self.edit_flask_time = []
        for i in range(5):
            _edit = my_line_edit(self.gb_flask)
            _edit.setFont(self.font16)
            _edit.setGeometry(QtCore.QRect(30 + 80 * i, 110, 51, 31))
            _edit.setAlignment(Qt.AlignCenter)
            _edit.setValidator(QDoubleValidator())
            self.edit_flask_time.append(_edit)

        self.gb_buff = my_gb(self.tab_poe1)
        self.gb_buff.setFont(self.font12)
        self.gb_buff.setGeometry(QtCore.QRect(20, 190, 431, 161))

        self.edit_buff_key = []
        for i in range(5):
            _edit = focus_line_edit(self.gb_buff, event, 'buff', i)
            _edit.setFont(self.font36)
            _edit.setGeometry(QtCore.QRect(30 + 80 * i, 30, 51, 71))
            _edit.setAlignment(Qt.AlignCenter)
            _edit.setReadOnly(True)
            self.edit_buff_key.append(_edit)

        self.edit_buff_time = []
        for i in range(5):
            _edit = my_line_edit(self.gb_buff)
            _edit.setFont(self.font16)
            _edit.setGeometry(QtCore.QRect(30 + 80 * i, 110, 51, 31))
            _edit.setAlignment(Qt.AlignCenter)
            _edit.setValidator(QDoubleValidator())
            self.edit_buff_time.append(_edit)

        self.gb_trigger = my_gb(self.tab_poe1)
        self.gb_trigger.setFont(self.font12)
        self.gb_trigger.setGeometry(QtCore.QRect(20, 370, 431, 121))

        self.edit_trigger_key = []
        for i in range(3):
            _edit = focus_line_edit(self.gb_trigger, event, 'trigger', i)
            _edit.setFont(self.font16)
            _edit.setGeometry(QtCore.QRect(30 + 130 * i, 30, 111, 71))
            _edit.setAlignment(Qt.AlignCenter)
            _edit.setReadOnly(True)
            self.edit_trigger_key.append(_edit)

        # POE2 tab
        self.gb_poe2_auto_flask = my_gb(self.tab_poe2)
        self.gb_poe2_auto_flask.setFont(self.font12)
        self.gb_poe2_auto_flask.setGeometry(QtCore.QRect(18, 12, 435, 135))

        self.cb_poe2_auto_enabled = QCheckBox(self.gb_poe2_auto_flask)
        self.cb_poe2_auto_enabled.setFont(self.font12)
        self.cb_poe2_auto_enabled.setGeometry(QtCore.QRect(20, 30, 160, 25))
        self.cb_poe2_auto_enabled.setVisible(False)
        self.cb_poe2_auto_enabled.setChecked(True)

        self.label_health_flask_key = my_label(self.gb_poe2_auto_flask)
        self.label_health_flask_key.setFont(self.font12)
        self.label_health_flask_key.setGeometry(QtCore.QRect(20, 80, 90, 25))

        self.edit_health_flask_key = focus_line_edit(self.gb_poe2_auto_flask, event, 'poe2_health_flask', 0)
        self.edit_health_flask_key.setFont(self.font16)
        self.edit_health_flask_key.setGeometry(QtCore.QRect(115, 78, 64, 30))
        self.edit_health_flask_key.setAlignment(Qt.AlignCenter)
        self.edit_health_flask_key.setReadOnly(True)

        self.label_mana_flask_key = my_label(self.gb_poe2_auto_flask)
        self.label_mana_flask_key.setFont(self.font12)
        self.label_mana_flask_key.setGeometry(QtCore.QRect(228, 80, 90, 25))

        self.edit_mana_flask_key = focus_line_edit(self.gb_poe2_auto_flask, event, 'poe2_mana_flask', 0)
        self.edit_mana_flask_key.setFont(self.font16)
        self.edit_mana_flask_key.setGeometry(QtCore.QRect(324, 78, 64, 30))
        self.edit_mana_flask_key.setAlignment(Qt.AlignCenter)
        self.edit_mana_flask_key.setReadOnly(True)

        self.gb_poe2_thresholds = my_gb(self.tab_poe2)
        self.gb_poe2_thresholds.setFont(self.font12)
        self.gb_poe2_thresholds.setGeometry(QtCore.QRect(18, 156, 435, 96))

        self.label_health_threshold = my_label(self.gb_poe2_thresholds)
        self.label_health_threshold.setFont(self.font12)
        self.label_health_threshold.setGeometry(QtCore.QRect(22, 40, 108, 25))

        self.edit_health_threshold = my_line_edit(self.gb_poe2_thresholds)
        self.edit_health_threshold.setFont(self.font12)
        self.edit_health_threshold.setGeometry(QtCore.QRect(134, 38, 70, 30))
        self.edit_health_threshold.setAlignment(Qt.AlignCenter)
        self.edit_health_threshold.setValidator(QIntValidator(10, 90))

        self.label_mana_threshold = my_label(self.gb_poe2_thresholds)
        self.label_mana_threshold.setFont(self.font12)
        self.label_mana_threshold.setGeometry(QtCore.QRect(230, 40, 108, 25))

        self.edit_mana_threshold = my_line_edit(self.gb_poe2_thresholds)
        self.edit_mana_threshold.setFont(self.font12)
        self.edit_mana_threshold.setGeometry(QtCore.QRect(342, 38, 70, 30))
        self.edit_mana_threshold.setAlignment(Qt.AlignCenter)
        self.edit_mana_threshold.setValidator(QIntValidator(10, 90))

        self.gb_poe2_status = my_gb(self.tab_poe2)
        self.gb_poe2_status.setFont(self.font12)
        self.gb_poe2_status.setGeometry(QtCore.QRect(18, 262, 435, 118))

        self.label_current_health = my_label(self.gb_poe2_status)
        self.label_current_health.setFont(self.font12)
        self.label_current_health.setGeometry(QtCore.QRect(24, 34, 170, 30))

        self.label_current_mana = my_label(self.gb_poe2_status)
        self.label_current_mana.setFont(self.font12)
        self.label_current_mana.setGeometry(QtCore.QRect(24, 70, 170, 30))

        self.label_flask_status = my_label(self.gb_poe2_status)
        self.label_flask_status.setFont(self.font12)
        self.label_flask_status.setGeometry(QtCore.QRect(208, 44, 205, 32))
        self.label_flask_status.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Form)
        self.apply_poe2_visual_style()
        self.init_config_combobox()
        self.load_setting(event)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.event_connect(event)
        self.choose_set(0)

    def event_connect(self, event):
        self.btn_start.clicked.connect(event.btn_start)
        self.btn_new_config.clicked.connect(event.btn_new_config)
        self.edit_new_config.returnPressed.connect(lambda: self.btn_new_config.click())
        self.combo_config.currentIndexChanged.connect(event.combo_config)
        self.btn_rename_config.clicked.connect(event.btn_rename_config)
        self.btn_save_config.clicked.connect(event.btn_save_config)
        self.btn_del_config.clicked.connect(event.btn_del_config)
        self.btn_floating_win.clicked.connect(event.btn_floating_win)

        self.tab_widget.currentChanged.connect(event.tab_changed)
        self.edit_health_threshold.editingFinished.connect(event.edit_health_threshold_changed)
        self.edit_mana_threshold.editingFinished.connect(event.edit_mana_threshold_changed)

        self.edit_flask_time[0].editingFinished.connect(lambda: event.time_edited(self.edit_flask_time[0]))
        self.edit_flask_time[1].editingFinished.connect(lambda: event.time_edited(self.edit_flask_time[1]))
        self.edit_flask_time[2].editingFinished.connect(lambda: event.time_edited(self.edit_flask_time[2]))
        self.edit_flask_time[3].editingFinished.connect(lambda: event.time_edited(self.edit_flask_time[3]))
        self.edit_flask_time[4].editingFinished.connect(lambda: event.time_edited(self.edit_flask_time[4]))
        self.edit_buff_time[0].editingFinished.connect(lambda: event.time_edited(self.edit_buff_time[0]))
        self.edit_buff_time[1].editingFinished.connect(lambda: event.time_edited(self.edit_buff_time[1]))
        self.edit_buff_time[2].editingFinished.connect(lambda: event.time_edited(self.edit_buff_time[2]))
        self.edit_buff_time[3].editingFinished.connect(lambda: event.time_edited(self.edit_buff_time[3]))
        self.edit_buff_time[4].editingFinished.connect(lambda: event.time_edited(self.edit_buff_time[4]))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("MainWindow", "POE 自动喝药"))
        self.label_ver.setText(_translate("MainWindow", now_version()))
        self.btn_start.setText(_translate("MainWindow", "开始"))
        self.btn_new_config.setText(_translate("MainWindow", "新建配置"))
        self.btn_rename_config.setText(_translate("MainWindow", "重命名"))
        self.btn_save_config.setText(_translate("MainWindow", "保存配置"))
        self.btn_del_config.setText(_translate("MainWindow", "删除配置"))
        self.btn_floating_win.setText(_translate("MainWindow", "悬浮窗"))

        self.gb_global.setTitle(_translate("MainWindow", "开关键"))
        self.edit_new_config.setPlaceholderText(_translate("MainWindow", "配置名称"))

        self.gb_flask.setTitle(_translate("MainWindow", "药水按键与间隔"))
        self.gb_buff.setTitle(_translate("MainWindow", "Buff按键与间隔"))
        self.gb_trigger.setTitle(_translate("MainWindow", "触发按键（为空则自动）"))

        self.gb_poe2_auto_flask.setTitle(_translate("MainWindow", "POE2 自动药水"))
        self.cb_poe2_auto_enabled.setText(_translate("MainWindow", "启用自动药水"))
        self.label_health_flask_key.setText(_translate("MainWindow", "血瓶按键"))
        self.label_mana_flask_key.setText(_translate("MainWindow", "蓝瓶按键"))

        self.gb_poe2_thresholds.setTitle(_translate("MainWindow", "触发阈值"))
        self.label_health_threshold.setText(_translate("MainWindow", "血量阈值(%)"))
        self.label_mana_threshold.setText(_translate("MainWindow", "蓝量阈值(%)"))

        self.gb_poe2_status.setTitle(_translate("MainWindow", "实时状态"))
        self.label_current_health.setText(_translate("MainWindow", "当前血量: ---%"))
        self.label_current_mana.setText(_translate("MainWindow", "当前蓝量: ---%"))
        self.label_flask_status.setText(_translate("MainWindow", "药水状态: 待机"))

    def apply_poe2_visual_style(self):
        self.tab_widget.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #343840; background: #1f2024; }"
            "QTabBar::tab { background: #2a2d33; color: #a8afbd; border: 1px solid #353a43; padding: 6px 14px; min-width: 80px; }"
            "QTabBar::tab:selected { background: #3a4250; color: #eef3ff; }"
        )

        card_css = (
            "QGroupBox {"
            " color: #eef2fb; border: 1px solid #404754; border-radius: 10px;"
            " margin-top: 12px; padding-top: 12px; background: #272c35; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; font-weight: 600; }"
        )
        self.gb_poe2_auto_flask.setStyleSheet(card_css)
        self.gb_poe2_thresholds.setStyleSheet(card_css)
        self.gb_poe2_status.setStyleSheet(card_css)

        label_css = "QLabel { color: #c6ceda; background: transparent; }"
        self.label_health_flask_key.setStyleSheet(label_css)
        self.label_mana_flask_key.setStyleSheet(label_css)
        self.label_health_threshold.setStyleSheet(label_css)
        self.label_mana_threshold.setStyleSheet(label_css)

        self.cb_poe2_auto_enabled.setStyleSheet(
            "QCheckBox { color: #e9edf5; spacing: 8px; font-weight: 600; }"
        )

        edit_css = (
            "QLineEdit {"
            " background: #161a20; border: 1px solid #5c6677; border-radius: 6px;"
            " color: #f8fbff; selection-background-color: #4a90e2; }"
        )
        self.edit_health_flask_key.setStyleSheet(edit_css)
        self.edit_mana_flask_key.setStyleSheet(edit_css)
        self.edit_health_threshold.setStyleSheet(edit_css)
        self.edit_mana_threshold.setStyleSheet(edit_css)

        self.label_current_health.setStyleSheet("QLabel {color: #f17b7b; background: transparent; font-weight: 600;}")
        self.label_current_mana.setStyleSheet("QLabel {color: #74b6ff; background: transparent; font-weight: 600;}")
        self.label_flask_status.setStyleSheet(
            "QLabel { color: #eef4ff; background: #2f3744; border: 1px solid #536179; border-radius: 9px; font-weight: 600; }"
        )

    def init_config_combobox(self):
        self.combo_config.addItems(self.main.config_list)

    def enable_edit(self, enable, fonction='all'):
        if fonction.startswith('a') and not enable:
            self.btn_start.setEnabled(enable)
            self.combo_config.setEnabled(enable)
            self.gb_global.setEnabled(enable)
            self.gb_flask.setEnabled(enable)
            self.gb_buff.setEnabled(enable)
            self.gb_trigger.setEnabled(enable)
            self.btn_rename_config.setEnabled(enable)
            self.btn_del_config.setEnabled(enable)
            self.btn_save_config.setEnabled(enable)
            self.gb_poe2_auto_flask.setEnabled(enable)
            self.gb_poe2_thresholds.setEnabled(enable)
            self.gb_poe2_status.setEnabled(enable)
        else:
            can_edit = self.main.is_editOK()
            self.btn_start.setEnabled(enable)
            self.btn_rename_config.setEnabled(can_edit)
            self.btn_del_config.setEnabled(can_edit)
            self.btn_save_config.setEnabled(can_edit)
            self.combo_config.setEnabled(can_edit)
            self.gb_global.setEnabled(can_edit)
            self.gb_flask.setEnabled(can_edit)
            self.gb_buff.setEnabled(can_edit)
            self.gb_trigger.setEnabled(can_edit)
            self.gb_poe2_auto_flask.setEnabled(can_edit)
            self.gb_poe2_thresholds.setEnabled(can_edit)
            self.gb_poe2_status.setEnabled(can_edit)

    def choose_set(self, index):
        for i in range(5):
            self.sets_index_labels[i].setStyleSheet('QLabel {background-color: #242424; color: #E6E6E6;}')
            self.sets_index_labels[i].setText('^' if self.main.set_enabel_status[i] else '')
        self.sets_index_labels[index].setText('^')
        self.sets_index_labels[index].setStyleSheet('QLabel {background-color: #242424; color: #20E620;}')

    def new_config(self, config_name):
        self.edit_new_config.setText('')
        self.enable_edit(True)
        self.combo_config.addItem(config_name)

    def load_setting(self, event):
        config_name = self.main.config_name
        if config_name == '':
            self.enable_edit(False)
            return

        set_index = event.current_set_index
        global_enable_key = self.main.from_setting('global', 'key', 'str')
        flask_key_list = self.main.from_setting('flask', f'key{set_index}', 'list')
        flask_time_list = self.main.from_setting('flask', f'time{set_index}', 'list')
        buff_key_list = self.main.from_setting('buff', f'key{set_index}', 'list')
        buff_time_list = self.main.from_setting('buff', f'time{set_index}', 'list')
        trigger_key_list = self.main.from_setting('trigger', f'key{set_index}', 'list')

        idx = self.combo_config.findText(config_name)
        self.combo_config.setCurrentIndex(idx)

        for i, key in enumerate(flask_key_list):
            self.edit_flask_key[i].setText(key)
            self.edit_flask_time[i].setEnabled(key != '')
        for i, dt in enumerate(flask_time_list):
            self.edit_flask_time[i].setText(dt)

        for i, key in enumerate(buff_key_list):
            self.edit_buff_key[i].setText(key)
            self.edit_buff_time[i].setEnabled(key != '')
        for i, dt in enumerate(buff_time_list):
            self.edit_buff_time[i].setText(dt)

        for i, key in enumerate(trigger_key_list):
            self.edit_trigger_key[i].setText(key)

        self.edit_global_enable_key.setText(global_enable_key)

        health_threshold = self.main.from_setting('poe2_auto_flask', 'health_threshold', 'str')
        mana_threshold = self.main.from_setting('poe2_auto_flask', 'mana_threshold', 'str')
        health_flask_key = self.main.from_setting('poe2_auto_flask', 'health_flask_key', 'str')
        mana_flask_key = self.main.from_setting('poe2_auto_flask', 'mana_flask_key', 'str')

        self.cb_poe2_auto_enabled.setChecked(True)
        self.edit_health_threshold.setText(health_threshold)
        self.edit_mana_threshold.setText(mana_threshold)
        self.edit_health_flask_key.setText(health_flask_key)
        self.edit_mana_flask_key.setText(mana_flask_key)

        self.enable_edit(True, '')

    def update_poe2_status(self, health_percent, mana_percent, flask_status="待机"):
        self.label_current_health.setText(f"当前血量: {health_percent:.0f}%")
        self.label_current_mana.setText(f"当前蓝量: {mana_percent:.0f}%")
        self.label_flask_status.setText(f"药水状态: {flask_status}")

        if health_percent <= 35:
            self.label_current_health.setStyleSheet("QLabel {color: #ff5f5f; background: transparent; font-weight: 700;}")
        elif health_percent <= 65:
            self.label_current_health.setStyleSheet("QLabel {color: #ff9a5c; background: transparent; font-weight: 600;}")
        else:
            self.label_current_health.setStyleSheet("QLabel {color: #f17b7b; background: transparent; font-weight: 600;}")

        if mana_percent <= 30:
            self.label_current_mana.setStyleSheet("QLabel {color: #66a3ff; background: transparent; font-weight: 700;}")
        else:
            self.label_current_mana.setStyleSheet("QLabel {color: #74b6ff; background: transparent; font-weight: 600;}")

        low_state = (health_percent <= 35) or (mana_percent <= 30) or ('health' in flask_status.lower()) or ('mana' in flask_status.lower())
        if low_state:
            self.label_flask_status.setStyleSheet("QLabel {color: #fff4f4; background: #6e3441; border: 1px solid #a45a6a; border-radius: 9px; font-weight: 700;}")
        else:
            self.label_flask_status.setStyleSheet("QLabel {color: #eef4ff; background: #2f3744; border: 1px solid #536179; border-radius: 9px; font-weight: 600;}")

    def get_current_tab(self):
        return self.tab_widget.currentIndex()
