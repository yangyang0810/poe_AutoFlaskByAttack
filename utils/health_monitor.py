import time
from PIL import ImageGrab
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


class HealthMonitor(QThread):
    """Health and mana monitoring system for POE games."""

    health_changed = pyqtSignal(float)
    mana_changed = pyqtSignal(float)
    flask_trigger = pyqtSignal(str)  # 'health' or 'mana'

    def __init__(self, poe_detector):
        super().__init__()
        self.poe_detector = poe_detector

        self.current_health = 1.0
        self.current_mana = 1.0

        self.health_threshold = 0.7
        self.mana_threshold = 0.5
        self.check_interval = 0.2
        self.last_check_time = 0
        self.monitoring = False
        self.current_mode = 'poe1'
        self.debug_enabled = False

        # Smoothing + anti-false-trigger controls
        self.ema_alpha = 0.45
        self.trigger_confirm_frames = 2
        self.low_health_frames = 0
        self.low_mana_frames = 0
        self.health_initialized = False
        self.mana_initialized = False

        # Relative screenshot regions in window coordinates
        self.bar_configs = {
            'poe1': {
                'health': {'x_start': 0.01, 'y_start': 0.88, 'x_end': 0.20, 'y_end': 0.95},
                'mana': {'x_start': 0.80, 'y_start': 0.88, 'x_end': 0.99, 'y_end': 0.95},
            },
            'poe2': {
                # Wider/taller orb ROI to cover inner liquid region across resolutions
                # Health: shrink from right by 1/5 of original width.
                # Mana: shrink from left by 1/5 of original width.
                'health': {'x_start': 0.012, 'y_start': 0.80, 'x_end': 0.1184, 'y_end': 0.985},
                'mana': {'x_start': 0.8816, 'y_start': 0.80, 'x_end': 0.988, 'y_end': 0.985},
            },
        }

    def set_current_mode(self, mode):
        self.current_mode = mode
        print(f"Health monitor set to {mode} mode")

    def set_health_threshold(self, threshold):
        try:
            threshold = float(threshold)
            self.health_threshold = max(0.1, min(0.9, threshold))
        except (ValueError, TypeError):
            self.health_threshold = 0.7

    def set_mana_threshold(self, threshold):
        try:
            threshold = float(threshold)
            self.mana_threshold = max(0.1, min(0.9, threshold))
        except (ValueError, TypeError):
            self.mana_threshold = 0.5

    def set_check_interval(self, interval):
        try:
            interval = float(interval)
            self.check_interval = max(0.1, min(1.0, interval))
        except (ValueError, TypeError):
            self.check_interval = 0.2

    def set_debug_enabled(self, enabled):
        self.debug_enabled = bool(enabled)

    def get_current_health(self):
        return self.current_health

    def get_current_mana(self):
        return self.current_mana

    def is_low_health(self):
        return self.current_health <= self.health_threshold

    def is_low_mana(self):
        return self.current_mana <= self.mana_threshold

    def get_bar_region(self, bar_config):
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
        except Exception:
            return None

    def analyze_health_bar(self, image):
        try:
            if image is None:
                return 1.0

            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0

            if self.current_mode == 'poe2':
                return self._estimate_orb_fill(image, color='red')

            # Legacy POE1 estimator
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                h, w = img_array.shape[:2]
                red_mask = (
                    (img_array[:, :, 0] > 60)
                    & (img_array[:, :, 1] < 180)
                    & (img_array[:, :, 2] < 180)
                    & (img_array[:, :, 0] > img_array[:, :, 1])
                    & (img_array[:, :, 0] > img_array[:, :, 2])
                )
                total = h * w
                if total == 0:
                    return 1.0
                return float(min(1.0, max(0.0, (np.sum(red_mask) / total) * 1.4)))

            return 1.0
        except Exception as e:
            print(f"Error analyzing health orb: {e}")
            return 1.0

    def analyze_mana_bar(self, image):
        try:
            if image is None:
                return 1.0

            img_array = np.array(image)
            if img_array.size == 0:
                return 1.0

            if self.current_mode == 'poe2':
                return self._estimate_orb_fill(image, color='blue')

            # Legacy POE1 estimator
            if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                h, w = img_array.shape[:2]
                blue_mask = (
                    (img_array[:, :, 0] < 180)
                    & (img_array[:, :, 1] < 180)
                    & (img_array[:, :, 2] > 60)
                    & (img_array[:, :, 2] > img_array[:, :, 0])
                    & (img_array[:, :, 2] > img_array[:, :, 1])
                )
                total = h * w
                if total == 0:
                    return 1.0
                return float(min(1.0, max(0.0, (np.sum(blue_mask) / total) * 1.4)))

            return 1.0
        except Exception as e:
            print(f"Error analyzing mana orb: {e}")
            return 1.0

    def _estimate_orb_fill(self, image, color='red'):
        """POE2 orb fill estimation using HSV mask + circle mask.

        Combines area ratio and bottom-up fill-height estimate for robustness.
        """
        try:
            rgb = np.array(image).astype('int16')
            hsv = np.array(image.convert('HSV')).astype('int16')
            if hsv.size == 0 or len(hsv.shape) < 3 or hsv.shape[2] < 3:
                return 1.0

            h, w = hsv.shape[:2]
            cy, cx = h // 2, w // 2
            radius = int(0.46 * min(h, w))

            yy, xx = np.ogrid[:h, :w]
            circle_mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= radius * radius

            H = hsv[:, :, 0]
            S = hsv[:, :, 1]
            V = hsv[:, :, 2]

            if color == 'red':
                # Red wraps around hue range in HSV.
                color_mask = (((H <= 18) | (H >= 235)) & (S >= 55) & (V >= 35))
            else:
                # Blue band tuned for POE2 mana orb.
                color_mask = ((H >= 130) & (H <= 185) & (S >= 45) & (V >= 28))

            mask = color_mask & circle_mask

            circle_pixels = int(np.sum(circle_mask))
            if circle_pixels <= 0:
                return 1.0

            area_ratio = float(np.sum(mask)) / float(circle_pixels)

            # Estimate liquid level by row coverage, then scan bottom-up.
            row_total = np.sum(circle_mask, axis=1).astype('float32')
            row_color = np.sum(mask, axis=1).astype('float32')
            valid_rows = row_total > 0
            row_cov = np.zeros_like(row_total, dtype='float32')
            row_cov[valid_rows] = row_color[valid_rows] / row_total[valid_rows]

            kernel = np.ones(5, dtype='float32') / 5.0
            row_cov_s = np.convolve(row_cov, kernel, mode='same')

            if np.any(valid_rows):
                p90 = float(np.percentile(row_cov_s[valid_rows], 90))
            else:
                p90 = 0.0
            row_thr = max(0.06, p90 * 0.32)
            row_on = row_cov_s >= row_thr

            idx_valid = np.where(valid_rows)[0]
            if idx_valid.size == 0:
                return 1.0
            top_i, bot_i = int(idx_valid[0]), int(idx_valid[-1])

            run = 0
            gap = 0
            max_gap = 2
            for i in range(bot_i, top_i - 1, -1):
                if not valid_rows[i]:
                    continue
                if row_on[i]:
                    run += 1
                    gap = 0
                else:
                    gap += 1
                    if gap > max_gap:
                        break

            fill_height = float(run) / float(max(1, bot_i - top_i + 1))

            # Combined score: area is stable, height tracks liquid boundary.
            hsv_ratio = 0.58 * area_ratio + 0.42 * fill_height

            # Fallback to legacy dominance estimate when HSV is weak/noisy.
            R = rgb[:, :, 0]
            G = rgb[:, :, 1]
            B = rgb[:, :, 2]
            if color == 'red':
                dom = R - np.maximum(G, B)
                legacy_thr = 0.22
            else:
                dom = B - np.maximum(R, G)
                legacy_thr = 0.14
            dom = np.maximum(dom, 0)
            dom_in = dom[circle_mask]
            if dom_in.size > 0:
                p95 = float(np.percentile(dom_in, 95))
                scale = max(30.0, p95)
                norm = np.clip(dom_in / scale, 0.0, 1.0)
                legacy_ratio = float((norm >= legacy_thr).mean())
            else:
                legacy_ratio = hsv_ratio

            # Prefer HSV but keep legacy as safety net.
            filled_ratio = max(0.72 * hsv_ratio + 0.28 * legacy_ratio, legacy_ratio * 0.88)
            return float(min(1.0, max(0.0, filled_ratio)))
        except Exception as e:
            print(f"Error in orb estimation: {e}")
            return 1.0

    def update_health_mana(self):
        try:
            if not self.poe_detector.check_immediately():
                return

            game_config = self.bar_configs.get(self.current_mode, self.bar_configs['poe1'])

            health_region = self.get_bar_region(game_config['health'])
            if health_region:
                health_screenshot = ImageGrab.grab(health_region)

                if not hasattr(self, 'health_screenshot_saved'):
                    health_screenshot.save('debug_health_screenshot.png')
                    print(f"Saved health debug screenshot: {health_region}, size={health_screenshot.size}")
                    self.health_screenshot_saved = True

                raw_health = self.analyze_health_bar(health_screenshot)
                new_health = self.ema_alpha * raw_health + (1.0 - self.ema_alpha) * self.current_health

                old_health = self.current_health
                self.current_health = new_health
                # Update UI more reliably for POE2 even when variation is small.
                if (not self.health_initialized) or abs(new_health - old_health) > 0.01:
                    self.health_changed.emit(new_health)
                    self.health_initialized = True

                if self.debug_enabled:
                    print(f"[POE2] Health: {self.current_health * 100:.0f}% (raw={raw_health * 100:.0f}%)")

                if self.is_low_health():
                    self.low_health_frames += 1
                else:
                    self.low_health_frames = 0
                if self.low_health_frames >= self.trigger_confirm_frames:
                    self.flask_trigger.emit('health')

            mana_region = self.get_bar_region(game_config['mana'])
            if mana_region:
                mana_screenshot = ImageGrab.grab(mana_region)

                if not hasattr(self, 'mana_screenshot_saved'):
                    mana_screenshot.save('debug_mana_screenshot.png')
                    print(f"Saved mana debug screenshot: {mana_region}, size={mana_screenshot.size}")
                    self.mana_screenshot_saved = True

                raw_mana = self.analyze_mana_bar(mana_screenshot)
                new_mana = self.ema_alpha * raw_mana + (1.0 - self.ema_alpha) * self.current_mana

                old_mana = self.current_mana
                self.current_mana = new_mana
                if (not self.mana_initialized) or abs(new_mana - old_mana) > 0.01:
                    self.mana_changed.emit(new_mana)
                    self.mana_initialized = True

                if self.debug_enabled:
                    print(f"[POE2] Mana: {self.current_mana * 100:.0f}% (raw={raw_mana * 100:.0f}%)")

                if self.is_low_mana():
                    self.low_mana_frames += 1
                else:
                    self.low_mana_frames = 0
                if self.low_mana_frames >= self.trigger_confirm_frames:
                    self.flask_trigger.emit('mana')

        except Exception as e:
            print(f"Error updating health/mana: {e}")

    def start_monitoring(self):
        self.monitoring = True
        if not self.isRunning():
            self.start()

    def stop_monitoring(self):
        self.monitoring = False
        if self.isRunning():
            self.quit()
            self.wait()

    def run(self):
        while self.monitoring:
            try:
                now = time.time()
                if now - self.last_check_time >= self.check_interval:
                    self.update_health_mana()
                    self.last_check_time = now

                if self.current_health <= 0.2:
                    time.sleep(0.05)
                elif self.current_health <= 0.5:
                    time.sleep(0.1)
                else:
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error in health monitor loop: {e}")
                time.sleep(0.1)
