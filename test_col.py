import sys
import os
import cv2
import numpy as np

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from image_processing import preprocess_image, detect_regions
from graph_builder import build_adjacency_graph
from coloring import color_graph
from renderer import render_colored_map

def test():
    image_path = "image.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        print("Failed to load image.")
        return

    print("Image loaded:", image_bgr.shape)
    
    gray, line_mask = preprocess_image(image_bgr)
    print("Preprocessed image.")
    
    region_labels, region_ids = detect_regions(line_mask)
    print(f"Detected {len(region_ids)} regions.")
    
    adjacency = build_adjacency_graph(region_labels, region_ids)
    print("Built adjacency graph:", adjacency)
    
    coloring = color_graph(adjacency, max_colors=4)
    if coloring is None:
        print("Failed to color graph with 4 colors.")
    else:
        print("Successfully colored graph.")
        print(coloring)

if __name__ == "__main__":
    test()
