import os
import sys
from datetime import datetime
from typing import List, Tuple

from PIL import Image

# Local imports
from utils.health_monitor import HealthMonitor


class _DummyDetector:
    """Minimal detector placeholder for HealthMonitor constructor."""

    pass


def _list_png_files(directory_path: str) -> List[str]:
    """Return a list of absolute paths for all .png files in the directory."""

    try:
        file_names = [
            name for name in os.listdir(directory_path)
            if name.lower().endswith(".png")
        ]
    except FileNotFoundError:
        return []

    return [os.path.join(directory_path, name) for name in sorted(file_names)]


def _classify_image(file_path: str) -> str:
    """Classify the image type by file name: 'health', 'mana', or 'unknown'."""

    lower_name = os.path.basename(file_path).lower()
    if "health" in lower_name:
        return "health"
    if "mana" in lower_name:
        return "mana"
    return "unknown"


def _analyze_image(monitor: HealthMonitor, file_path: str) -> Tuple[str, float, float]:
    """Analyze a single image and return (type, health_pct, mana_pct).

    For 'health' images, mana_pct will be -1. For 'mana' images, health_pct will be -1.
    For 'unknown', both will be computed.
    """

    image = Image.open(file_path).convert("RGB")
    image_type = _classify_image(file_path)

    health_pct: float = -1.0
    mana_pct: float = -1.0

    def estimate_bar_fill(img, color: str) -> float:
        """Estimate bar fill using combined column score and area ratio for robustness."""
        import numpy as np

        arr = np.array(img).astype("int16")
        h, w = arr.shape[:2]

        # Central 70% height band to reduce border noise
        top = int(h * 0.15)
        bottom = int(h * 0.85)
        band = arr[top:bottom, :, :]

        r = band[:, :, 0]
        g = band[:, :, 1]
        b = band[:, :, 2]

        if color == "red":
            dom = r - np.maximum(g, b)
        else:
            dom = b - np.maximum(r, g)

        dom = np.maximum(dom, 0)
        col_score = dom.mean(axis=0) / 255.0

        # Smooth a little
        k = 5
        if w >= k:
            kernel = np.ones(k) / k
            col_score = np.convolve(col_score, kernel, mode="same")

        # Relative threshold based on max to better catch bright full bars
        max_v = float(col_score.max())
        if max_v > 1e-6:
            norm = col_score / max_v
        else:
            norm = col_score
        rel_thr = 0.20
        filled_cols_ratio = float((norm >= rel_thr).mean())

        # Longest consecutive segment above a low threshold (captures continuous bars)
        low_thr = 0.08
        above = (norm >= low_thr).astype("int32")
        if above.any():
            # Compute run lengths
            max_run = 0
            cur = 0
            for v in above:
                if v:
                    cur += 1
                    if cur > max_run:
                        max_run = cur
                else:
                    cur = 0
            run_ratio = max_run / max(1, norm.shape[0])
        else:
            run_ratio = 0.0

        # Area-based simple color dominance mask
        if color == "red":
            area_mask = (r > g + 10) & (r > b + 10) & (r > 80)
        else:
            area_mask = (b > g + 5) & (b > r + 5) & (b > 70)
        area_ratio = float(area_mask.mean())
        if color == "red":
            # Favor full bars: allow any robust criterion to dominate
            fill_ratio = max(filled_cols_ratio, run_ratio, min(1.0, area_ratio * 1.2))
        else:
            # Be conservative for mana to avoid overestimation on thin traces
            fill_ratio = min(max(filled_cols_ratio, run_ratio * 0.9), min(1.0, area_ratio * 2.0))
        return float(min(1.0, max(0.0, fill_ratio)))

    def estimate_orb_fill(img, color: str) -> float:
        """Estimate orb fill within a central circle using color dominance and adaptive threshold."""
        import numpy as np

        arr = np.array(img).astype("int16")
        h, w = arr.shape[:2]
        cy, cx = h // 2, w // 2
        radius = int(0.45 * min(h, w))

        yy, xx = np.ogrid[:h, :w]
        circle_mask = (yy - cy) ** 2 + (xx - cx) ** 2 <= radius * radius

        R = arr[:, :, 0]
        G = arr[:, :, 1]
        B = arr[:, :, 2]

        if color == "red":
            dom = R - np.maximum(G, B)
        else:
            dom = B - np.maximum(R, G)
        dom = np.maximum(dom, 0)

        dom_in = dom[circle_mask]
        if dom_in.size == 0:
            return 0.0

        # Normalize by robust scale (95th percentile) to reduce highlight bias
        p95 = float(np.percentile(dom_in, 95))
        scale = max(30.0, p95)  # ensure minimal scale to avoid tiny denominators
        norm = np.clip(dom_in / scale, 0.0, 1.0)

        # Thresholds tuned: higher for red (full), lower for blue (thin remains)
        thr = 0.22 if color == "red" else 0.14
        filled_ratio = float((norm >= thr).mean())

        # If the orb is largely filled for blue, boost toward 100%
        if color == "blue":
            high_thr = 0.6
            high_cover = float((norm >= high_thr).mean())
            if high_cover >= 0.6:
                filled_ratio = max(filled_ratio, 0.98)

        # Calibration: ensure small but non-zero when blue exists
        if color == "blue" and dom_in.max() > 0 and filled_ratio < 0.04:
            filled_ratio = 0.05

        return float(min(1.0, max(0.0, filled_ratio)))

    lower_name = os.path.basename(file_path).lower()

    if image_type in ("health", "unknown"):
        if "health_bar" in lower_name:
            # health_bar_* are orb crops, use orb estimator
            health_pct = estimate_orb_fill(image, "red")
        else:
            health_pct = float(monitor.analyze_health_bar(image))

    if image_type in ("mana", "unknown"):
        if "mana_bar" in lower_name:
            # mana_bar_* are orb crops, use orb estimator
            mana_pct = estimate_orb_fill(image, "blue")
        else:
            mana_pct = float(monitor.analyze_mana_bar(image))

    return image_type, health_pct, mana_pct


def _format_pct(value: float) -> str:
    """Format a percentage value in [0,1] to 'XX.X%'; return '-' when negative."""

    if value < 0:
        return "-"
    return f"{value * 100:.1f}%"


def main() -> int:
    """Entry point: analyze images in debug_screenshots and write result.log."""

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    screenshots_dir = os.path.join(project_root, "debug_screenshots")
    log_path = os.path.join(screenshots_dir, "result.log")

    files = _list_png_files(screenshots_dir)

    monitor = HealthMonitor(_DummyDetector())

    lines: List[str] = []
    lines.append(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Directory: {screenshots_dir}")
    lines.append("")

    if not files:
        lines.append("No PNG files found.")
    else:
        lines.append("File, Type, Health, Mana")
        for file_path in files:
            try:
                image_type, health_pct, mana_pct = _analyze_image(monitor, file_path)
                lines.append(
                    ", ".join(
                        [
                            os.path.basename(file_path),
                            image_type,
                            _format_pct(health_pct),
                            _format_pct(mana_pct),
                        ]
                    )
                )
            except Exception as exc:
                lines.append(f"{os.path.basename(file_path)}, error, -, -  # {exc}")

    content = "\n".join(lines) + "\n"

    os.makedirs(screenshots_dir, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Result written to: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


