import threading
import time

from pynput import mouse
from pynput import keyboard
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from utils.health_monitor import HealthMonitor

class trigger_move_button(QPushButton):
    def __init__(self, parent):
        QPushButton.__init__(self, parent)

class flaskbuff():
    def __init__(self, key, cdt, trigger_type='time', health_threshold=0.3):
        self.key = key
        self.cdt = cdt
        self.trigger_time = time.time() - cdt
        self.trigger_type = trigger_type  # 'time', 'health', 'emergency'
        self.health_threshold = health_threshold
        self.priority = 5  # Default priority

    def trigger(self):
        trigger_time = time.time()
        if trigger_time - self.trigger_time > self.cdt: # not using
            self.trigger_time = trigger_time
            return True, self.cdt
        else:
            return False, self.cdt - (trigger_time - self.trigger_time)

    def should_trigger_by_health(self, current_health, current_mana=1.0):
        """Check if flask should trigger based on health/mana"""
        # First check if cooldown allows triggering
        can_trigger, _ = self.trigger()
        if not can_trigger:
            return False
        
        if self.trigger_type == 'health':
            return current_health <= self.health_threshold
        elif self.trigger_type == 'emergency':
            return current_health <= 0.15  # Emergency threshold
        elif self.trigger_type == 'mana':
            return current_mana <= self.health_threshold
        
        return False

    def press(self):
        return self.key

class Delaybuff(flaskbuff):
    def __init__(self, key, cdt):
        super().__init__(key, cdt)
        self.delay_mode = True
        self.delay_time = cdt
        self.cdt = 0.1

    def trigger(self):
        trigger_time = time.time()
        if trigger_time - self.trigger_time > self.cdt: # not using
            self.trigger_time = trigger_time
            if self.delay_mode:
                self.trigger_time += self.delay_time
                self.delay_mode = False
                return False
            return True
        else:
            return False

    def key_release(self):
        self.delay_mode = True

class input_listener():
    def __init__(self, main):
        self.main = main  # Store main reference
        self.start_move_floating = main.start_move_floating
        self.start_stop = main.event.btn_start
        self.is_working = getattr(main, 'is_working')
        self.is_setting = getattr(main, 'is_setting')
        self.ui = getattr(main, 'ui')

        self.con = threading.Condition()
        self.btn_signal = trigger_move_button(main)
        self.btn_signal.setGeometry(QRect(0, 0, 0, 0))
        self.btn_signal.clicked.connect(main.event.change_floating_border)

        self.keyboard = keyboard.Controller()
        self.mouse_listener = mouse.Listener(on_move = self.mouse_on_move, on_click = self.mouse_on_click, on_scroll = self.mouse_on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press = self.keyboard_on_press, on_release = self.keyboard_on_release)

        self.MOUSE_MAIN_SCREEN = True
        self.last_button = ''
        self.switch_button = ''
        self.sets = [{"trigger_button":[], "buff":[]} for _ in range(5)]
        self.trigger_set_index = [] # for notify loop thread which set is triggered
        self.auto_sets = []
        self.health_sets = []  # Sets with health-triggered flasks
        self.t_auto = threading.Thread(target=self.run_auto,)
        
        # Initialize health monitor
        self.health_monitor = HealthMonitor(main.detector)
        self.health_monitoring_enabled = False
        
        # Connect to flask trigger signal
        self.health_monitor.flask_trigger.connect(self.on_flask_trigger)
        self.last_health_flask_time = 0
        self.last_mana_flask_time = 0
        self.health_flask_cooldown = 3.0  # 3 second cooldown for health flask
        self.mana_flask_cooldown = 3.0    # 3 second cooldown for mana flask

    def button_regularization(self, btn):
        return str(btn).split('.')[-1].replace("'",'')

    def button_unregularization(self, btn):
        if len(btn) > 1:
            if btn in ['left', 'right', 'x1', 'x2', 'middle']:
                return 'Button.' + btn
            else:
                return 'Key.' + btn
        else:
            return btn

    def get_last(self):
        _temp = self.last_button
        self.last_button = ''
        return _temp

    def load_and_start(self, setting):
        switch = setting['switch']
        flasks = setting['flask_key']
        flask_times = setting['flask_time']
        buffs = setting['buff_key']
        buff_times = setting['buff_time']
        triggers = setting['trigger_key']
        
        # Get health-related settings
        health_flasks = setting.get('health_flask_key', [[] for _ in range(5)])
        health_thresholds = setting.get('health_threshold', [[] for _ in range(5)])
        health_flask_times = setting.get('health_flask_time', [[] for _ in range(5)])
        emergency_flasks = setting.get('emergency_flask_key', [[] for _ in range(5)])
        emergency_flask_times = setting.get('emergency_flask_time', [[] for _ in range(5)])
        
        self.switch_button = switch
        self.auto_sets.clear()
        self.health_sets.clear()
        
        # Stop existing auto thread
        if self.t_auto.is_alive():
            self.t_auto._stop_event = threading.Event()
            self.t_auto._stop_event.set()
        
        # Check if health monitoring should be enabled
        self.health_monitoring_enabled = any(
            any(health_flasks[i]) or any(emergency_flasks[i]) for i in range(5)
        )
        
        for set_index, set in enumerate(self.sets):
            set["buff"].clear()
            set["trigger_button"].clear()
            has_health_flasks = False
            
            # Regular time-based flasks
            for f_index, key in enumerate(flasks[set_index]):
                if flask_times[set_index][f_index] != '':
                    set["buff"].append(flaskbuff(key, float(flask_times[set_index][f_index]), 'time'))
            
            # Regular time-based buffs
            for b_index, key in enumerate(buffs[set_index]):
                if buff_times[set_index][b_index] != '':
                    set["buff"].append(flaskbuff(key, float(buff_times[set_index][b_index]), 'time'))
            
            # Health-based flasks
            if set_index < len(health_flasks):
                for h_index, key in enumerate(health_flasks[set_index]):
                    if key != '' and h_index < len(health_flask_times[set_index]) and health_flask_times[set_index][h_index] != '':
                        threshold = 0.3  # Default threshold
                        if h_index < len(health_thresholds[set_index]) and health_thresholds[set_index][h_index] != '':
                            try:
                                threshold = float(health_thresholds[set_index][h_index]) / 100.0
                            except:
                                threshold = 0.3
                        
                        health_flask = flaskbuff(key, float(health_flask_times[set_index][h_index]), 'health', threshold)
                        health_flask.priority = 8  # Higher priority for health flasks
                        set["buff"].append(health_flask)
                        has_health_flasks = True
            
            # Emergency flasks
            if set_index < len(emergency_flasks):
                for e_index, key in enumerate(emergency_flasks[set_index]):
                    if key != '' and e_index < len(emergency_flask_times[set_index]) and emergency_flask_times[set_index][e_index] != '':
                        emergency_flask = flaskbuff(key, float(emergency_flask_times[set_index][e_index]), 'emergency')
                        emergency_flask.priority = 10  # Highest priority
                        set["buff"].append(emergency_flask)
                        has_health_flasks = True
            
            # Set up trigger buttons
            for t_index, key in enumerate(triggers[set_index]):
                if key != '':
                    set["trigger_button"].append(key)
            
            # Categorize sets
            if len(set["trigger_button"]) == 0 and len(set["buff"]) > 0: 
                self.auto_sets.append(set)
            if has_health_flasks:
                self.health_sets.append(set)
        
        # Start monitoring threads
        if len(self.auto_sets) > 0 or len(self.health_sets) > 0:
            self.t_auto = threading.Thread(target=self.run_auto,)
            self.t_auto.setDaemon(True)
            self.t_auto.start()
        
        # Start health monitoring if needed
        if self.health_monitoring_enabled:
            self.health_monitor.start_monitoring()
        
        # Also start health monitoring for POE2 auto flask
        poe2_enabled = self.main.from_setting('poe2_auto_flask', 'enabled', 'bool')
        if poe2_enabled:
            # Set thresholds from config
            try:
                health_threshold = self.main.from_setting('poe2_auto_flask', 'health_threshold', 'int') / 100.0
                mana_threshold = self.main.from_setting('poe2_auto_flask', 'mana_threshold', 'int') / 100.0
                check_interval = self.main.from_setting('poe2_auto_flask', 'check_interval', 'str')
                
                # Load cooldown settings
                health_cooldown = float(self.main.from_setting('poe2_auto_flask', 'health_flask_cooldown', 'str'))
                mana_cooldown = float(self.main.from_setting('poe2_auto_flask', 'mana_flask_cooldown', 'str'))
                
                self.health_monitor.set_health_threshold(health_threshold)
                self.health_monitor.set_mana_threshold(mana_threshold)
                self.health_monitor.set_check_interval(check_interval)
                self.health_monitor.set_debug_enabled(True)  # Enable debug for troubleshooting
                
                # Set cooldown times
                self.health_flask_cooldown = health_cooldown
                self.mana_flask_cooldown = mana_cooldown
                
                self.health_monitor.start_monitoring()
                print(f"POE2 health monitoring started - Health threshold: {health_threshold*100:.0f}%, Mana threshold: {mana_threshold*100:.0f}%")
                print(f"Cooldowns - Health: {health_cooldown}s, Mana: {mana_cooldown}s")
            except Exception as e:
                print(f"Error setting up POE2 health monitoring: {e}")
                # Use default values
                self.health_monitor.set_health_threshold(0.75)
                self.health_monitor.set_mana_threshold(0.55)
                self.health_monitor.set_check_interval(0.2)
                self.health_monitor.set_debug_enabled(True)
                self.health_monitor.start_monitoring()
                print("POE2 health monitoring started with default values")

    def mouse_on_move(self, x, y):
        pass
        # if x > 1920:
        #     self.MOUSE_MAIN_SCREEN = False
        # else:
        #     self.MOUSE_MAIN_SCREEN = True


    def mouse_on_click(self, x, y , button, pressed):
        button = self.button_regularization(button)
        trigger_buttons = [btn for set in self.sets for btn in set["trigger_button"]]
        if self.is_setting():
            self.last_button = button
        elif button == trigger_buttons and pressed:
            self.start_stop()
        elif not self.is_working():
            return
        # print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
        # print(button)
        elif button in trigger_buttons:
            if pressed:
                self.trigger_set_index = [i for i ,set in enumerate(self.sets) for btn in set["trigger_button"] if btn == button]
                with self.con:
                    self.con.notify()

    def mouse_on_scroll(self, x, y ,dx, dy):
        pass
        # print('scrolled {0} at {1}'.format(qw
        #     'down' if dy < 0 else 'up',
        #     (x, y)))

    def keyboard_on_press(self, button):
        button = self.button_regularization(button)
        trigger_buttons = [btn for set in self.sets for btn in set["trigger_button"]]
        if button in ['up', 'down', 'left', 'right']:
            return
        elif button == 'alt_l':
            self.start_move_floating(True)
            self.btn_signal.click()
        elif self.is_setting():
            self.last_button = button
        elif button == self.switch_button:
            self.start_stop()
        elif not self.is_working():
            return
        elif button in trigger_buttons:
            self.trigger_set_index = [i for i ,set in enumerate(self.sets) for btn in set["trigger_button"] if btn == button]
            with self.con:
                self.con.notify()

    def keyboard_on_release(self, button):
        button = self.button_regularization(button)
        if button == 'alt_l':
            self.start_move_floating(False)
            self.btn_signal.click()
        if not self.is_working():
            return

    def start(self):
        self.t = threading.Thread(target=self.run,)
        self.t.setDaemon(True)
        self.t.start()

    def run(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        while True:
            self.con.acquire()
            self.con.wait()
            for set_index in self.trigger_set_index:
                for buff in self.sets[set_index]["buff"]:
                    if self.is_working():
                        if buff.trigger()[0]:
                            self.keyboard.press(self.button_unregularization(buff.press()))
                            self.keyboard.release(self.button_unregularization(buff.press()))

    def run_auto(self):
        while True:
            sleep_min = 0.1  # Minimum sleep for health checking
            
            if self.is_working():
                current_health = 1.0
                current_mana = 1.0
                
                # Get current health/mana if monitoring is enabled
                if self.health_monitoring_enabled and self.health_monitor:
                    current_health = self.health_monitor.get_current_health()
                    current_mana = self.health_monitor.get_current_mana()
                
                # Process health-triggered flasks first (higher priority)
                health_flasks_used = []
                for health_set in self.health_sets:
                    # Sort by priority (emergency flasks first)
                    health_buffs = [buff for buff in health_set["buff"] if buff.trigger_type in ['health', 'emergency', 'mana']]
                    health_buffs.sort(key=lambda x: getattr(x, 'priority', 5), reverse=True)
                    
                    for buff in health_buffs:
                        if buff.should_trigger_by_health(current_health, current_mana):
                            self.keyboard.press(self.button_unregularization(buff.press()))
                            self.keyboard.release(self.button_unregularization(buff.press()))
                            health_flasks_used.append(buff.key)
                            # Only use one health flask per cycle to avoid spam
                            if buff.trigger_type == 'emergency':
                                break
                
                # Process regular time-based flasks
                for auto_set in self.auto_sets:
                    for buff in auto_set["buff"]:
                        if buff.trigger_type == 'time':  # Only process time-based buffs here
                            TRIGGER, sleep_time = buff.trigger()
                            if sleep_time < sleep_min: 
                                sleep_min = sleep_time
                            if TRIGGER:
                                self.keyboard.press(self.button_unregularization(buff.press()))
                                self.keyboard.release(self.button_unregularization(buff.press()))
                
                # Adjust sleep time based on health status
                if current_health <= 0.2:
                    sleep_min = min(sleep_min, 0.05)  # Very frequent checking when low health
                elif current_health <= 0.5:
                    sleep_min = min(sleep_min, 0.1)   # More frequent checking
                else:
                    sleep_min = max(sleep_min, 0.2)   # Less frequent when healthy
            
            time.sleep(sleep_min)

    def on_flask_trigger(self, flask_type):
        """Handle automatic flask trigger based on health/mana thresholds"""
        current_time = time.time()
        
        # Check if POE2 auto flask is enabled
        poe2_enabled = self.main.from_setting('poe2_auto_flask', 'enabled', 'bool')
        if not poe2_enabled:
            return
        
        # Check if we're in POE2 mode or auto mode
        current_mode = getattr(self.main, 'current_mode', 'poe1')
        if current_mode not in ['poe2', 'auto']:
            return
        
        try:
            if flask_type == 'health':
                # Check cooldown for health flask (3 seconds)
                if current_time - self.last_health_flask_time < self.health_flask_cooldown:
                    remaining_time = self.health_flask_cooldown - (current_time - self.last_health_flask_time)
                    print(f"Health flask on cooldown, {remaining_time:.1f}s remaining")
                    return
                
                health_flask_key = self.main.from_setting('poe2_auto_flask', 'health_flask_key', 'str')
                if health_flask_key:
                    # Add random delay (0-100ms)
                    import random
                    random_delay = random.uniform(0, 0.1)
                    time.sleep(random_delay)
                    
                    self.simulate_key_press(health_flask_key)
                    self.last_health_flask_time = current_time
                    print(f"Auto triggered health flask: {health_flask_key} (delay: {random_delay*1000:.1f}ms)")
            
            elif flask_type == 'mana':
                # Check cooldown for mana flask (3 seconds)
                if current_time - self.last_mana_flask_time < self.mana_flask_cooldown:
                    remaining_time = self.mana_flask_cooldown - (current_time - self.last_mana_flask_time)
                    print(f"Mana flask on cooldown, {remaining_time:.1f}s remaining")
                    return
                
                mana_flask_key = self.main.from_setting('poe2_auto_flask', 'mana_flask_key', 'str')
                if mana_flask_key:
                    # Add random delay (0-100ms)
                    import random
                    random_delay = random.uniform(0, 0.1)
                    time.sleep(random_delay)
                    
                    self.simulate_key_press(mana_flask_key)
                    self.last_mana_flask_time = current_time
                    print(f"Auto triggered mana flask: {mana_flask_key} (delay: {random_delay*1000:.1f}ms)")
                    
        except Exception as e:
            print(f"Error triggering flask: {e}")
    
    def simulate_key_press(self, key):
        """Simulate a key press using multiple methods"""
        try:
            import time
            import win32api
            import win32con
            import win32gui
            
            # 确保游戏窗口有焦点
            if hasattr(self.main, 'detector') and self.main.detector.poe_hWnd:
                win32gui.SetForegroundWindow(self.main.detector.poe_hWnd)
                time.sleep(0.1)  # 等待窗口切换
            
            # 方法1: 尝试 pydirectinput
            try:
                import pydirectinput
                pydirectinput.press(key)
                print(f"Successfully pressed key (pydirectinput): {key}")
                return
            except Exception as e:
                print(f"pydirectinput failed: {e}")
            
            # 方法2: 使用 Windows API 作为备用
            try:
                # 将字符转换为虚拟键码
                if key.isdigit():
                    vk_code = ord(key)
                else:
                    vk_code = ord(key.upper())
                
                # 按下按键
                win32api.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.05)
                # 释放按键
                win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
                print(f"Successfully pressed key (Windows API): {key}")
                
            except Exception as e:
                print(f"Windows API failed: {e}")
                raise e
            
        except Exception as e:
            print(f"Error simulating key press {key}: {e}")

    def join(self):
        self.t.join()