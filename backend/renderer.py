import cv2
import base64
import numpy as np
from typing import Dict

FOUR_COLORS_RGB = [
    (255, 99, 71),    # Tomato
    (60, 179, 113),   # Green
    (65, 105, 225),   # Blue
    (255, 215, 0),    # Yellow
]


def render_colored_map(
    original_bgr: np.ndarray,
    line_mask: np.ndarray,
    region_labels: np.ndarray,
    coloring: Dict[int, int]
) -> np.ndarray:
    """
    Fill regions according to coloring, then redraw black boundaries on top.
    """
    output = np.ones_like(original_bgr, dtype=np.uint8) * 255

    region_ids = [rid for rid in np.unique(region_labels) if rid != 0]
    for rid in region_ids:
        color_idx = coloring.get(int(rid), 0)
        rgb = FOUR_COLORS_RGB[color_idx]
        bgr = (rgb[2], rgb[1], rgb[0])
        output[region_labels == rid] = bgr

    output[line_mask > 0] = (0, 0, 0)
    return output


def make_debug_region_image(region_labels: np.ndarray) -> np.ndarray:
    """
    Visual debug image where each region gets a random color.
    """
    out = np.zeros((region_labels.shape[0], region_labels.shape[1], 3), dtype=np.uint8)
    rng = np.random.default_rng(42)

    for rid in np.unique(region_labels):
        if rid == 0:
            continue
        color = rng.integers(50, 255, size=3, dtype=np.uint8)
        out[region_labels == rid] = color

    return out


def encode_image_to_base64_png(image_bgr: np.ndarray) -> str:
    """
    Encode OpenCV BGR image as base64 PNG for JSON response.
    """
    success, buffer = cv2.imencode(".png", image_bgr)
    if not success:
        raise ValueError("Failed to encode image.")
    encoded = base64.b64encode(buffer.tobytes()).decode("utf-8")
    return encoded