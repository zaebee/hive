import json
from collections import deque
from typing import Dict, List, Any

def build_adjacency_list(components: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Builds an adjacency list representation of the component graph."""
    graph = {}
    for comp in components:
        comp_id = comp.get("id")
        if comp_id:
            graph[comp_id] = comp.get("connections", [])
    return graph

def calculate_architectural_hops(graph: Dict[str, List[str]], start_node: str, end_node: str) -> int:
    """
    Calculates the shortest path (number of hops) between two nodes in a graph.

    Uses a Breadth-First Search (BFS) algorithm. This represents 'r', the
    architectural distance, in our physics models.

    Args:
        graph: An adjacency list representation of the Hive's component graph.
        start_node: The ID of the starting component.
        end_node: The ID of the ending component.

    Returns:
        The number of hops in the shortest path.
        Returns -1 if there is no path between the nodes.
        Returns 0 if start_node and end_node are the same.
    """
    if start_node == end_node:
        return 0

    if start_node not in graph or end_node not in graph:
        raise ValueError(f"Node '{start_node if start_node not in graph else end_node}' not found in the graph.")

    queue = deque([(start_node, 0)])  # A queue of (node, distance)
    visited = {start_node}

    while queue:
        current_node, distance = queue.popleft()

        for neighbor in graph.get(current_node, []):
            if neighbor == end_node:
                return distance + 1

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    return -1  # No path found

if __name__ == '__main__':
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    print("--- Calculating Architectural Distance (Hops) ---")

    try:
        with open(mock_file_path, 'r') as f:
            data = json.load(f)

        components = data.get("hive_snapshot", {}).get("components", [])
        component_graph = build_adjacency_list(components)

        print("\nComponent Graph (Adjacency List):")
        for node, connections in component_graph.items():
            print(f"  - {node}: {connections}")

        # Test cases
        test_pairs = [
            ("comp_001", "comp_004"), # Should be 3 hops (1->2->3->4)
            ("comp_001", "comp_002"), # Should be 1 hop
            ("comp_001", "comp_001"), # Should be 0 hops
            ("comp_001", "comp_005")  # Non-existent node, should raise error
        ]

        for start, end in test_pairs:
            try:
                print(f"\nCalculating distance between '{start}' and '{end}'...")
                hops = calculate_architectural_hops(component_graph, start, end)
                if hops != -1:
                    print(f"  - Shortest Path: {hops} hops")
                else:
                    print(f"  - No path found between '{start}' and '{end}'.")
            except ValueError as e:
                print(f"  - Error: {e}")

    except FileNotFoundError:
        print(f"Error: Could not find mock data file at '{mock_file_path}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
