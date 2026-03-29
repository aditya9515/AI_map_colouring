import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from image_processing import preprocess_image, detect_regions
from graph_builder import build_adjacency_graph
from coloring import color_graph

def run():
    image_bgr = cv2.imread("image.png")
    gray, line_mask = preprocess_image(image_bgr)
    region_labels, region_ids = detect_regions(line_mask)
    adjacency = build_adjacency_graph(region_labels, region_ids)
    
    coloring = color_graph(adjacency, max_colors=4)
    if not coloring:
        print("COLORING_FAILED")
        return
    
    # Verify coloring
    valid = True
    for node, color in coloring.items():
        for neighbor in adjacency[node]:
            if coloring.get(neighbor) == color:
                print(f"INVALID: {node} and {neighbor} have same color {color}")
                valid = False
    
    import json
    # Print a summary of connections for node 1 to verify graph
    connections = {k: list(v) for k, v in adjacency.items() if k in [1, 2, 3]}
    print("Graph subset:", json.dumps(connections))
                
    if valid:
        print("COLORING_VALID")
    else:
        print("COLORING_INVALID")

run()
