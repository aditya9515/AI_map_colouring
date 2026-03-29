import numpy as np
import cv2
from main import segment_image, color_graph

# Create a dummy image: 3 regions separated by a black line
image = np.ones((100, 100, 3), dtype=np.uint8) * 255
cv2.line(image, (50, 0), (50, 100), (0, 0, 0), 3)
cv2.line(image, (50, 50), (100, 50), (0, 0, 0), 3)

labels, _ = segment_image(image)
unique_labels = np.unique(labels[labels != 0])
graph = {int(i): set() for i in unique_labels}
kernel = np.ones((21, 21), np.uint8)

print("Unique labels:", unique_labels)
for label in unique_labels:
    mask = (labels == label).astype(np.uint8)
    print(f"Mask {label} size:", np.sum(mask))
    dilated = cv2.dilate(mask, kernel, iterations=1)
    print(f"Dilated {label} size:", np.sum(dilated))
    intersecting_labels = np.unique(labels[dilated > 0])
    print(f"intersecting_labels for {label}:", intersecting_labels)
    for neighbor in intersecting_labels:
        if neighbor != 0 and neighbor != label:
            graph[int(label)].add(int(neighbor))
            graph[int(neighbor)].add(int(label))

print("Graph:", graph)
