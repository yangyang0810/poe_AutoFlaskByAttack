import time
import threading
from PIL import ImageGrab
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class HealthMonitor(QThread):
    """Health monitoring system for POE game"""
    health_changed = pyqtSignal(float)  # Signal emitted when health changes significantly
    
    def __init__(self, poe_detector):
        super().__init__()
        self.poe_detector = poe_detector
        self.current_health = 1.0
        self.current_mana = 1.0
        self.health_threshold = 0.3  # Default 30% health threshold
        self.emergency_threshold = 0.15  # Emergency 15% threshold
        self.check_interval = 0.1  # Check every 100ms
        self.last_check_time = 0
        self.monitoring = False
        
        # Health bar coordinates (relative to game window)
        # These may need adjustment based on game resolution and UI scale
        self.health_bar_relative = {
            'x_start': 0.02,   # 2% from left edge
            'y_start': 0.85,   # 85% from top
            'x_end': 0.25,     # 25% from left edge  
            'y_end': 0.90      # 90% from top
        }
        
        # Mana bar coordinates
        self.mana_bar_relative = {
            'x_start': 0.02,
            'y_start': 0.90,
            'x_end': 0.25,
            'y_end': 0.95
        }
    
    def set_health_threshold(self, threshold):
        """Set health threshold (0.0 to 1.0)"""
        self.health_threshold = max(0.1, min(0.8, threshold))
    
    def set_emergency_threshold(self, threshold):
        """Set emergency threshold (0.0 to 1.0)"""
        self.emergency_threshold = max(0.05, min(0.3, threshold))
    
    def get_current_health(self):
        """Get current health percentage"""
        return self.current_health
    
    def get_current_mana(self):
        """Get current mana percentage"""
        return self.current_mana
    
    def is_low_health(self):
        """Check if health is below threshold"""
        return self.current_health <= self.health_threshold
    
    def is_emergency_health(self):
        """Check if health is in emergency range"""
        return self.current_health <= self.emergency_threshold
    
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
            
            # Get health bar region and screenshot
            health_region = self.get_bar_region(self.health_bar_relative)
            if health_region:
                health_screenshot = ImageGrab.grab(health_region)
                new_health = self.analyze_health_bar(health_screenshot)
                
                # Emit signal if health changed significantly
                if abs(new_health - self.current_health) > 0.05:
                    self.health_changed.emit(new_health)
                
                self.current_health = new_health
            
            # Get mana bar region and screenshot
            mana_region = self.get_bar_region(self.mana_bar_relative)
            if mana_region:
                mana_screenshot = ImageGrab.grab(mana_region)
                self.current_mana = self.analyze_mana_bar(mana_screenshot)
                
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
