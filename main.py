from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import networkx as nx
import base64

app = FastAPI()


# -----------------------------
# Utility: Encode image to base64
# -----------------------------
def encode_image(img):
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')


def convert_graph(graph):
    return {
        str(int(k)): [int(x) for x in v]
        for k, v in graph.items()
    }


def convert_assignment(assignment):
    return {
        str(int(k)): v
        for k, v in assignment.items()
    }


# -----------------------------
# Step 1: Image Segmentation
# -----------------------------
def segment_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 1: Detect lines (black boundaries)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Step 2: Make lines thicker (important)
    kernel = np.ones((3, 3), np.uint8)
    walls = cv2.dilate(thresh, kernel, iterations=2)

    # Step 3: Invert → regions become white spaces
    free_space = cv2.bitwise_not(walls)

    h, w = free_space.shape
    labels = np.zeros((h, w), dtype=np.int32)

    label_id = 1
    
    # Add black border around image
    line_mask[0, :] = 255
    line_mask[-1, :] = 255
    line_mask[:, 0] = 255
    line_mask[:, -1] = 255

    # Step 4: Flood fill each region
    for i in range(h):
        for j in range(w):
            if free_space[i, j] == 255 and labels[i, j] == 0:
                mask = np.zeros((h+2, w+2), np.uint8)
                cv2.floodFill(free_space, mask, (j, i), 128)

                # assign label
                labels[free_space == 128] = label_id

                # reset filled region
                free_space[free_space == 128] = 0

                label_id += 1

    return labels, label_id


# -----------------------------
# Step 2: Build Adjacency Graph
# -----------------------------
def build_graph(labels):
    h, w = labels.shape
    unique_labels = np.unique(labels)
    unique_labels = unique_labels[unique_labels != 0]

    graph = {int(i): set() for i in unique_labels}

    for i in range(h):
        for j in range(w):
            current = labels[i, j]

            for di, dj in [(1, 0), (0, 1)]:  # 4-connectivity
                ni, nj = i + di, j + dj
                if ni < h and nj < w:
                    neighbor = labels[ni, nj]
                    if current != neighbor:
                        graph[current].add(neighbor)
                        graph[neighbor].add(current)

    return graph


# -----------------------------
# Step 3: 4-Coloring (Backtracking)
# -----------------------------
COLORS = ["red", "green", "blue", "yellow"]


def is_safe(node, color, assignment, graph):
    for neighbor in graph[node]:
        if assignment.get(neighbor) == color:
            return False
    return True


def color_graph(graph):
    nodes = list(graph.keys())
    assignment = {}

    def backtrack(index):
        if index == len(nodes):
            return True

        node = nodes[index]

        for color in COLORS:
            if is_safe(node, color, assignment, graph):
                assignment[node] = color
                if backtrack(index + 1):
                    return True
                del assignment[node]

        return False

    backtrack(0)
    return assignment


# -----------------------------
# Step 4: Render Colored Image
# -----------------------------
COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0)
}


def render_image(labels, assignment):
    h, w = labels.shape
    output = np.zeros((h, w, 3), dtype=np.uint8)

    for region, color_name in assignment.items():
        output[labels == region] = COLOR_MAP[color_name]

    return output


# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/color-map/")
async def color_map(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Step 1: Segmentation
    labels, num_labels = segment_image(image)

    # Step 2: Graph
    graph = build_graph(labels)

    # Optional: Check Planarity
    G = nx.Graph()
    for node, neighbors in graph.items():
        for n in neighbors:
            G.add_edge(node, n)

    is_planar, _ = nx.check_planarity(G)

    # Step 3: Coloring
    assignment = color_graph(graph)

    # Step 4: Render
    colored_image = render_image(labels, assignment)

    # Encode images
    original_b64 = encode_image(image)
    segmented_vis = (labels.astype(np.float32) / labels.max() * 255).astype(np.uint8)
    segmented_b64 = encode_image(segmented_vis)
    output_b64 = encode_image(colored_image)

    return JSONResponse({
        "is_planar": bool(is_planar),
        "graph": convert_graph(graph),
        "coloring": convert_assignment(assignment),
        "original_image": original_b64,
        "segmented_image": segmented_b64,
        "colored_image": output_b64
    })
