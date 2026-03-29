from typing import Dict, Optional, Set

MAX_COLORS = 4


def is_valid_color(node: int, color_idx: int, coloring: Dict[int, int], adjacency: Dict[int, Set[int]]) -> bool:
    for neighbor in adjacency[node]:
        if coloring.get(neighbor) == color_idx:
            return False
    return True


def select_uncolored_node(coloring: Dict[int, int], adjacency: Dict[int, Set[int]]) -> Optional[int]:
    uncolored = [node for node in adjacency if node not in coloring]
    if not uncolored:
        return None
    return max(uncolored, key=lambda n: len(adjacency[n]))


def color_graph(adjacency: Dict[int, Set[int]], max_colors: int = MAX_COLORS) -> Optional[Dict[int, int]]:
    """
    Backtracking graph coloring with up to 4 colors.
    """
    coloring: Dict[int, int] = {}
    print("ADA Starting graph coloring with adjacency:", adjacency)

    def backtrack() -> bool:
        node = select_uncolored_node(coloring, adjacency)
        if node is None:
            return True

        for color_idx in range(max_colors):
            if is_valid_color(node, color_idx, coloring, adjacency):
                coloring[node] = color_idx
                if backtrack():
                    return True
                del coloring[node]

        return False

    success = backtrack()
    print("ADA colouring success:", success)
    print("ADA Coloring result:", coloring)
    return coloring if success else None