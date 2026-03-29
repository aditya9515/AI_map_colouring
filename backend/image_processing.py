import cv2
import numpy as np
from typing import List, Tuple

MIN_REGION_AREA = 150


def decode_image(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded image bytes into an OpenCV BGR image."""
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Invalid image file.")

    return image


def preprocess_image(image_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert image to grayscale and generate a binary boundary mask.

    Output:
    - gray: grayscale image
    - line_mask: white boundaries on black background
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Slight blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detection instead of raw thresholding
    edges = cv2.Canny(blurred, 50, 150)

    # Thicken edges
    kernel_dilate = np.ones((3, 3), np.uint8)
    line_mask = cv2.dilate(edges, kernel_dilate, iterations=2)

    # Close small breaks in boundaries
    kernel_close = np.ones((5, 5), np.uint8)
    line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_CLOSE, kernel_close, iterations=2)

    # Optional light opening to remove tiny specks
    kernel_open = np.ones((3, 3), np.uint8)
    line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_OPEN, kernel_open, iterations=1)

    return gray, line_mask


def detect_regions(line_mask: np.ndarray) -> Tuple[np.ndarray, List[int]]:
    """
    Detect enclosed regions inside a line drawing.

    Returns:
        filtered_labels: labeled region map, 0 = background/non-region
        region_ids: list of valid region IDs
    """
    h, w = line_mask.shape

    # Make a working copy
    line_mask = line_mask.copy()

    # Force image border to be closed so outside is separated
    line_mask[0, :] = 255
    line_mask[-1, :] = 255
    line_mask[:, 0] = 255
    line_mask[:, -1] = 255

    # Regions/spaces should be white, boundaries should be black
    spaces = cv2.bitwise_not(line_mask)

    # Flood fill from the outside corner
    flood = spaces.copy()
    flood_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(flood, flood_mask, (0, 0), 128)

    # Remaining white areas are enclosed regions
    enclosed = np.where(flood == 255, 255, 0).astype(np.uint8)

    # Connected components on enclosed regions
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        enclosed,
        connectivity=8
    )

    filtered_labels = np.zeros_like(labels, dtype=np.int32)
    region_ids: List[int] = []
    next_region_id = 1

    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]

        if area >= MIN_REGION_AREA:
            filtered_labels[labels == label_id] = next_region_id
            region_ids.append(next_region_id)
            next_region_id += 1

    return filtered_labels, region_ids