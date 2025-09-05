import time
import threading
from PIL import ImageGrab
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class HealthMonitor(QThread):
    """Health and mana monitoring system for POE games"""
    health_changed = pyqtSignal(float)  # Signal emitted when health changes significantly
    mana_changed = pyqtSignal(float)    # Signal emitted when mana changes significantly
    flask_trigger = pyqtSignal(str)     # Signal to trigger flask ('health' or 'mana')
    
    def __init__(self, poe_detector):
        super().__init__()
        self.poe_detector = poe_detector
        self.current_health = 1.0
        self.current_mana = 1.0
        self.health_threshold = 0.7  # Default 70% health threshold
        self.mana_threshold = 0.5    # Default 50% mana threshold
        self.check_interval = 0.2    # Check every 200ms
        self.last_check_time = 0
        self.monitoring = False
        self.current_mode = 'poe1'  # Default mode
        
        # Different bar positions for different games
        self.bar_configs = {
            'poe1': {
                'health': {
                    'x_start': 0.02, 'y_start': 0.85,
                    'x_end': 0.25, 'y_end': 0.90
                },
                'mana': {
                    'x_start': 0.02, 'y_start': 0.90,
                    'x_end': 0.25, 'y_end': 0.95
                }
            },
            'poe2': {
                'health': {
                    'x_start': 0.02, 'y_start': 0.88,  # May need adjustment for POE2
                    'x_end': 0.25, 'y_end': 0.93
                },
                'mana': {
                    'x_start': 0.75, 'y_start': 0.88,  # Mana might be on the right in POE2
                    'x_end': 0.98, 'y_end': 0.93
                }
            }
        }
    
    def set_current_mode(self, mode):
        """Set current game mode"""
        self.current_mode = mode
        print(f"Health monitor set to {mode} mode")
    
    def set_health_threshold(self, threshold):
        """Set health threshold (0.0 to 1.0)"""
        self.health_threshold = max(0.1, min(0.9, threshold))
    
    def set_mana_threshold(self, threshold):
        """Set mana threshold (0.0 to 1.0)"""
        self.mana_threshold = max(0.1, min(0.9, threshold))
    
    def set_check_interval(self, interval):
        """Set check interval in seconds"""
        self.check_interval = max(0.1, min(1.0, interval))
    
    def get_current_health(self):
        """Get current health percentage"""
        return self.current_health
    
    def get_current_mana(self):
        """Get current mana percentage"""
        return self.current_mana
    
    def is_low_health(self):
        """Check if health is below threshold"""
        return self.current_health <= self.health_threshold
    
    def is_low_mana(self):
        """Check if mana is below threshold"""
        return self.current_mana <= self.mana_threshold
    
    def get_bar_region(self, bar_config):
        """Calculate screen coordinates for health/mana bar"""
        try:
            poe_running, rect = self.poe_detector.get_poe_rect()
            if not poe_running:
                return None
                
            x1, y1, x2, y2 = rect
            w = x2 - x1
            h = y2 - y1
            
            bar_x1 = x1 + int(w * bar_config['x_start'])
            bar_y1 = y1 + int(h * bar_config['y_start'])
            bar_x2 = x1 + int(w * bar_config['x_end'])
            bar_y2 = y1 + int(h * bar_config['y_end'])
            
            return (bar_x1, bar_y1, bar_x2, bar_y2)
        except:
            return None
    
    def analyze_health_bar(self, image):
        """Analyze health bar image to get health percentage"""
        try:
            if image is None:
                return 1.0
                
            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0
            
            # Convert to RGB if needed
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                # Look for red pixels (health bar color)
                # Health bar is typically red: high R, low G, low B
                red_mask = (img_array[:, :, 0] > 120) & \
                          (img_array[:, :, 1] < 80) & \
                          (img_array[:, :, 2] < 80)
                
                total_width = img_array.shape[1]
                if total_width == 0:
                    return 1.0
                
                # Calculate percentage based on red pixels from left
                red_pixels_per_row = np.sum(red_mask, axis=0)
                
                # Find the rightmost red pixel
                red_columns = np.where(red_pixels_per_row > 0)[0]
                if len(red_columns) == 0:
                    return 0.0
                
                health_width = np.max(red_columns) + 1
                health_percentage = health_width / total_width
                
                return min(1.0, max(0.0, health_percentage))
            
            return 1.0
        except Exception as e:
            print(f"Error analyzing health bar: {e}")
            return 1.0
    
    def analyze_mana_bar(self, image):
        """Analyze mana bar image to get mana percentage"""
        try:
            if image is None:
                return 1.0
                
            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0
            
            # Convert to RGB if needed
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                # Look for blue pixels (mana bar color)
                # Mana bar is typically blue: low R, low G, high B
                blue_mask = (img_array[:, :, 0] < 80) & \
                           (img_array[:, :, 1] < 100) & \
                           (img_array[:, :, 2] > 120)
                
                total_width = img_array.shape[1]
                if total_width == 0:
                    return 1.0
                
                # Calculate percentage based on blue pixels from left
                blue_pixels_per_row = np.sum(blue_mask, axis=0)
                
                # Find the rightmost blue pixel
                blue_columns = np.where(blue_pixels_per_row > 0)[0]
                if len(blue_columns) == 0:
                    return 0.0
                
                mana_width = np.max(blue_columns) + 1
                mana_percentage = mana_width / total_width
                
                return min(1.0, max(0.0, mana_percentage))
            
            return 1.0
        except Exception as e:
            print(f"Error analyzing mana bar: {e}")
            return 1.0
    
    def update_health_mana(self):
        """Update current health and mana values"""
        try:
            # Only check if POE is active
            if not self.poe_detector.check_immediately():
                return
            
            # Get current game config based on mode
            game_config = self.bar_configs.get(self.current_mode, self.bar_configs['poe1'])
            
            # Monitor health
            health_region = self.get_bar_region(game_config['health'])
            if health_region:
                health_screenshot = ImageGrab.grab(health_region)
                new_health = self.analyze_health_bar(health_screenshot)
                
                # Check for significant health change
                if abs(new_health - self.current_health) > 0.05:  # 5% change threshold
                    self.current_health = new_health
                    self.health_changed.emit(new_health)
                else:
                    self.current_health = new_health
                
                # Check if health flask should be triggered
                if self.is_low_health():
                    self.flask_trigger.emit('health')
            
            # Monitor mana
            mana_region = self.get_bar_region(game_config['mana'])
            if mana_region:
                mana_screenshot = ImageGrab.grab(mana_region)
                new_mana = self.analyze_mana_bar(mana_screenshot)
                
                # Check for significant mana change
                if abs(new_mana - self.current_mana) > 0.05:  # 5% change threshold
                    self.current_mana = new_mana
                    self.mana_changed.emit(new_mana)
                else:
                    self.current_mana = new_mana
                
                # Check if mana flask should be triggered
                if self.is_low_mana():
                    self.flask_trigger.emit('mana')
                
        except Exception as e:
            print(f"Error updating health/mana: {e}")
    
    def start_monitoring(self):
        """Start health monitoring"""
        self.monitoring = True
        if not self.isRunning():
            self.start()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.isRunning():
            self.quit()
            self.wait()
    
    def run(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                current_time = time.time()
                if current_time - self.last_check_time >= self.check_interval:
                    self.update_health_mana()
                    self.last_check_time = current_time
                
                # Dynamic sleep based on health level
                if self.current_health <= 0.2:
                    time.sleep(0.05)  # Check more frequently when low health
                elif self.current_health <= 0.5:
                    time.sleep(0.1)   # Normal frequency
                else:
                    time.sleep(0.2)   # Less frequent when healthy
                    
            except Exception as e:
                print(f"Error in health monitor loop: {e}")
                time.sleep(0.1)
