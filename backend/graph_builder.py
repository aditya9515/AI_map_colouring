import cv2
import numpy as np
from typing import Dict, List, Set


def build_adjacency_graph(region_labels: np.ndarray, region_ids: List[int]) -> Dict[int, Set[int]]:
    """
    Build adjacency graph by dilating each region and checking which
    other region labels it touches.
    """
    adjacency: Dict[int, Set[int]] = {rid: set() for rid in region_ids}
    kernel = np.ones((3, 3), np.uint8)

    region_masks = {
        rid: (region_labels == rid).astype(np.uint8)
        for rid in region_ids
    }

    for rid1 in region_ids:
        dilated = cv2.dilate(region_masks[rid1], kernel, iterations=1)
        touched_labels = np.unique(region_labels[dilated > 0])

        for rid2 in touched_labels:
            rid2 = int(rid2)
            if rid2 != 0 and rid2 != rid1:
                adjacency[rid1].add(rid2)
                adjacency[rid2].add(rid1)

    return adjacency


def adjacency_to_json(adjacency: Dict[int, Set[int]]) -> Dict[str, List[int]]:
    """Convert set-based adjacency map into JSON-safe dict."""
    return {str(k): sorted(list(v)) for k, v in adjacency.items()}