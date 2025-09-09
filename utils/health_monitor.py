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
        self.debug_enabled = False  # Print debug percentages when enabled
        
        # Different bar positions for different games
        # Updated to focus on bottom-left health and bottom-right mana
        self.bar_configs = {
            'poe1': {
                'health': {
                    'x_start': 0.01, 'y_start': 0.88,  # Bottom-left corner
                    'x_end': 0.20, 'y_end': 0.95
                },
                'mana': {
                    'x_start': 0.80, 'y_start': 0.88,  # Bottom-right corner
                    'x_end': 0.99, 'y_end': 0.95
                }
            },
            'poe2': {
                'health': {
                    'x_start': 0.01, 'y_start': 0.82,  # Bottom-left corner (高度调高一倍)
                    'x_end': 0.115, 'y_end': 0.98  # 右边减少四分之一 (从15%到11.5%)
                },
                'mana': {
                    'x_start': 0.8875, 'y_start': 0.82,  # Bottom-right corner (高度调高一倍)
                    'x_end': 0.99, 'y_end': 0.98  # 右边减少四分之一 (从85%到88.75%)
                }
            }
        }
    
    def set_current_mode(self, mode):
        """Set current game mode"""
        self.current_mode = mode
        print(f"Health monitor set to {mode} mode")
    
    def set_health_threshold(self, threshold):
        """Set health threshold (0.0 to 1.0)"""
        try:
            threshold = float(threshold)
            self.health_threshold = max(0.1, min(0.9, threshold))
        except (ValueError, TypeError):
            self.health_threshold = 0.7  # Default value
    
    def set_mana_threshold(self, threshold):
        """Set mana threshold (0.0 to 1.0)"""
        try:
            threshold = float(threshold)
            self.mana_threshold = max(0.1, min(0.9, threshold))
        except (ValueError, TypeError):
            self.mana_threshold = 0.5  # Default value
    
    def set_check_interval(self, interval):
        """Set check interval in seconds"""
        try:
            interval = float(interval)
            self.check_interval = max(0.1, min(1.0, interval))
        except (ValueError, TypeError):
            self.check_interval = 0.2  # Default value
    
    def set_debug_enabled(self, enabled):
        """Enable or disable debug printing"""
        self.debug_enabled = bool(enabled)
    
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
        """Analyze health orb image to get health percentage"""
        try:
            if image is None:
                return 1.0
                
            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0
            
            # If poe2, prefer circular orb estimation within ROI
            if getattr(self, 'current_mode', 'poe1') == 'poe2':
                return self._estimate_orb_fill(image, color='red')

            # Convert to RGB if needed
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                height, width = img_array.shape[:2]
                
                # For circular orb, use pixel count method
                # Look for red pixels with flexible color range
                red_mask = (img_array[:, :, 0] > 60) & \
                          (img_array[:, :, 1] < 180) & \
                          (img_array[:, :, 2] < 180) & \
                          (img_array[:, :, 0] > img_array[:, :, 1]) & \
                          (img_array[:, :, 0] > img_array[:, :, 2])
                
                # Count total red pixels
                red_pixel_count = np.sum(red_mask)
                total_pixels = height * width
                
                if total_pixels == 0:
                    return 1.0
                
                # Calculate percentage based on red pixel ratio
                health_percentage = red_pixel_count / total_pixels
                
                # Scale to more reasonable range (since orb might not be 100% red)
                # Adjust this multiplier based on testing
                health_percentage = min(1.0, health_percentage * 1.4)
                
                # Add smoothing to reduce noise
                if hasattr(self, 'last_health_percentage'):
                    # Smooth with previous reading (60% current, 40% previous)
                    health_percentage = 0.6 * health_percentage + 0.4 * self.last_health_percentage
                
                self.last_health_percentage = health_percentage
                
                # Debug output for first few times
                if not hasattr(self, 'health_debug_count'):
                    self.health_debug_count = 0
                self.health_debug_count += 1
                
                if self.health_debug_count <= 5:
                    print(f"[DEBUG] Health: red_pixels={red_pixel_count}, total={total_pixels}, raw_ratio={red_pixel_count/total_pixels:.3f}, final={health_percentage:.3f}")
                
                return min(1.0, max(0.0, health_percentage))
            
            return 1.0
        except Exception as e:
            print(f"Error analyzing health orb: {e}")
            return 1.0
    
    def analyze_mana_bar(self, image):
        """Analyze mana orb image to get mana percentage"""
        try:
            if image is None:
                return 1.0
                
            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0
            
            # If poe2, prefer circular orb estimation within ROI
            if getattr(self, 'current_mode', 'poe1') == 'poe2':
                return self._estimate_orb_fill(image, color='blue')

            # Convert to RGB if needed
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                height, width = img_array.shape[:2]
                
                # For circular orb, use pixel count method
                # Look for blue pixels with flexible color range
                blue_mask = (img_array[:, :, 0] < 180) & \
                           (img_array[:, :, 1] < 180) & \
                           (img_array[:, :, 2] > 60) & \
                           (img_array[:, :, 2] > img_array[:, :, 0]) & \
                           (img_array[:, :, 2] > img_array[:, :, 1])
                
                # Count total blue pixels
                blue_pixel_count = np.sum(blue_mask)
                total_pixels = height * width
                
                if total_pixels == 0:
                    return 1.0
                
                # Calculate percentage based on blue pixel ratio
                mana_percentage = blue_pixel_count / total_pixels
                
                # Scale to more reasonable range (since orb might not be 100% blue)
                # Adjust this multiplier based on testing
                mana_percentage = min(1.0, mana_percentage * 1.4)
                
                # Add smoothing to reduce noise
                if hasattr(self, 'last_mana_percentage'):
                    # Smooth with previous reading (60% current, 40% previous)
                    mana_percentage = 0.6 * mana_percentage + 0.4 * self.last_mana_percentage
                
                self.last_mana_percentage = mana_percentage
                
                # Debug output for first few times
                if not hasattr(self, 'mana_debug_count'):
                    self.mana_debug_count = 0
                self.mana_debug_count += 1
                
                if self.mana_debug_count <= 5:
                    print(f"[DEBUG] Mana: blue_pixels={blue_pixel_count}, total={total_pixels}, raw_ratio={blue_pixel_count/total_pixels:.3f}, final={mana_percentage:.3f}")
                
                return min(1.0, max(0.0, mana_percentage))
            
            return 1.0
        except Exception as e:
            print(f"Error analyzing mana orb: {e}")
            return 1.0

    def _estimate_orb_fill(self, image, color='red'):
        """Estimate orb fill ratio within a central circular ROI using color dominance.

        color: 'red' for health, 'blue' for mana.
        """
        try:
            arr = np.array(image).astype('int16')
            if arr.size == 0 or len(arr.shape) < 3 or arr.shape[2] < 3:
                return 1.0

            h, w = arr.shape[:2]
            cy, cx = h // 2, w // 2
            radius = int(0.45 * min(h, w))

            yy, xx = np.ogrid[:h, :w]
            circle_mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= radius * radius

            R = arr[:, :, 0]
            G = arr[:, :, 1]
            B = arr[:, :, 2]

            if color == 'red':
                dom = R - np.maximum(G, B)
            else:
                dom = B - np.maximum(R, G)
            dom = np.maximum(dom, 0)

            dom_in = dom[circle_mask]
            if dom_in.size == 0:
                return 1.0

            # Normalize by robust percentile scale
            p95 = float(np.percentile(dom_in, 95)) if dom_in.size > 0 else 1.0
            scale = max(30.0, p95)
            norm = np.clip(dom_in / scale, 0.0, 1.0)

            # Threshold tuned from tests
            thr = 0.22 if color == 'red' else 0.14
            filled_ratio = float((norm >= thr).mean())

            if color == 'blue':
                # Boost when most of orb is bright
                high_thr = 0.6
                high_cover = float((norm >= high_thr).mean())
                if high_cover >= 0.6:
                    filled_ratio = max(filled_ratio, 0.98)
                # Ensure small but non-zero when present
                if dom_in.max() > 0 and filled_ratio < 0.04:
                    filled_ratio = 0.05

            # Clamp to [0,1]
            return float(min(1.0, max(0.0, filled_ratio)))
        except Exception as e:
            print(f"Error in orb estimation: {e}")
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
                
                # Save first health screenshot for debugging
                if not hasattr(self, 'health_screenshot_saved'):
                    health_screenshot.save('debug_health_screenshot.png')
                    print(f"💾 已保存血量截图: debug_health_screenshot.png")
                    print(f"📍 血量截图区域: {health_region}")
                    print(f"📏 血量截图尺寸: {health_screenshot.size}")
                    self.health_screenshot_saved = True
                
                new_health = self.analyze_health_bar(health_screenshot)
                
                # Check for significant health change
                if abs(new_health - self.current_health) > 0.05:  # 5% change threshold
                    self.current_health = new_health
                    self.health_changed.emit(new_health)
                else:
                    self.current_health = new_health
                
                # Debug print
                if self.debug_enabled:
                    print(f"[POE2] Health: {self.current_health*100:.0f}%")

                # Check if health flask should be triggered
                if self.is_low_health():
                    self.flask_trigger.emit('health')
            
            # Monitor mana
            mana_region = self.get_bar_region(game_config['mana'])
            if mana_region:
                mana_screenshot = ImageGrab.grab(mana_region)
                
                # Save first mana screenshot for debugging
                if not hasattr(self, 'mana_screenshot_saved'):
                    mana_screenshot.save('debug_mana_screenshot.png')
                    print(f"💾 已保存蓝量截图: debug_mana_screenshot.png")
                    print(f"📍 蓝量截图区域: {mana_region}")
                    print(f"📏 蓝量截图尺寸: {mana_screenshot.size}")
                    self.mana_screenshot_saved = True
                
                new_mana = self.analyze_mana_bar(mana_screenshot)
                
                # Check for significant mana change
                if abs(new_mana - self.current_mana) > 0.05:  # 5% change threshold
                    self.current_mana = new_mana
                    self.mana_changed.emit(new_mana)
                else:
                    self.current_mana = new_mana
                
                # Debug print
                if self.debug_enabled:
                    print(f"[POE2] Mana: {self.current_mana*100:.0f}%")

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
