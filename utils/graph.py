from functools import lru_cache
import os
from tkinter import messagebox, simpledialog, Toplevel, Button, Label
import numpy as np
from collections import deque


class Graph:
    def __init__(self):
        self.filename = "graph.txt"
        self.walkable_tiles = self.load_walkable_tiles()
        self.nodes = []
        self.edges = []  # This will now store (start, end, distance) tuples
        self.edge_labels = {}
        if os.path.exists(self.filename):
            self.load()

    def load_walkable_tiles(self):
        walkable = np.zeros((900, 4050), dtype=np.byte)
        with open("walkable_tiles.bin", "rb") as file:
            for i in range(900):
                for j in range(4050):
                    byte = file.read(1)
                    walkable[i][j] = 1 if ord(byte) > 0 else 0
        return walkable

    @lru_cache(None)
    def calculate_distance(self, start, end):
        queue = deque([(start, 0)])  # (position, distance)
        visited = set([start])
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left

        while queue:
            (x, y), distance = queue.popleft()
            if (x, y) == end:
                return distance

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited or self.walkable_tiles[nx][ny] == 0:
                    continue
                visited.add((nx, ny))
                queue.append(((nx, ny), distance + 1))

        return -1  # Return -1 if no path found

    def save(self):
        with open(self.filename, "w") as f:
            for edge in self.edges:
                # edge already includes distance as its third element
                f.write(
                    f"{edge[0][0]},{edge[0][1]},{edge[1][0]},{edge[1][1]},{edge[2]},{self.edge_labels.get(self.edge_to_string(edge), '')}\n"
                )
        messagebox.showinfo("Save", "Graph saved successfully.")

    def load(self):
        with open(self.filename, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                node1 = (int(parts[0]), int(parts[1]))
                node2 = (int(parts[2]), int(parts[3]))
                distance = int(parts[4])
                # Ensure nodes for the current edge are added
                if node1 not in self.nodes:
                    self.nodes.append(node1)
                if node2 not in self.nodes:
                    self.nodes.append(node2)
                self.edges.append((node1, node2, distance))
                # Add label if exists
                label = parts[5] if len(parts) > 5 else ""
                if label:
                    self.edge_labels[self.edge_to_string((node1, node2, distance))] = (
                        label
                    )

    def edge_to_string(self, edge):
        # Adapted to handle (node1, node2, distance) format
        return f"{edge[0][0]},{edge[0][1]}-{edge[1][0]},{edge[1][1]}"

    def create_edge(self, node_from, node_to):
        dist = self.calculate_distance(node_from, node_to)
        if dist == -1 or dist > 25:
            if messagebox.askyesno(
                "No Path Found",
                "Override?",
            ):
                dist = -1
            else:
                return False
        edge = (node_from, node_to, dist)  # Now includes distance or override
        if edge not in self.edges:
            self.edges.append(edge)
        return True

    def edit_edge(self, edge, uimaster, redraw):
        from tkinter import Toplevel, Button

        class EditEdgeDialog(Toplevel):
            def __init__(self, graph, master):
                super().__init__(master)
                self.graph = graph
                Label(self, text=f"Edit Edge \"{graph.edge_labels.get(graph.edge_to_string(edge), '')}\"").pack(fill="x")
                Label(self, text=f"Current dist: {edge[2]}").pack(fill="x")
                Button(self, text="Delete Edge", command=self.delete_edge).pack(
                    fill="x"
                )
                Button(self, text="Change Label", command=self.change_label).pack(
                    fill="x"
                )
                Button(
                    self, text="Override Distance", command=self.override_distance
                ).pack(fill="x")

            def delete_edge(self):
                self.graph.delete_edge(edge)
                redraw()
                self.destroy()

            def change_label(self):
                new_label = simpledialog.askstring(
                    "Change Label", "Enter new label:", parent=self
                )
                if new_label:
                    self.graph.edge_labels[self.graph.edge_to_string(edge)] = (
                        new_label
                    )
                    redraw()
                    self.destroy()

            def override_distance(self):
                new_distance = simpledialog.askinteger(
                    "Override Distance", "Enter new distance:", parent=self
                )
                if new_distance is not None:
                    for i, e in enumerate(self.graph.edges):
                        if e[:2] == edge[:2]:  # Matching the edge to override
                            self.graph.edges[i] = (e[0], e[1], new_distance)
                            break
                    self.destroy()

        dialog = EditEdgeDialog(
            self, uimaster
        )  # Make sure uimaster is your Tkinter main window or a widget.

    def delete_node(self, node):
        self.nodes.remove(node)
        # Remove connected edges and labels
        edges_to_remove = self.edges_connected(node)
        for edge in edges_to_remove:
            self.edges.remove(edge)
            edge_key = self.edge_to_string(edge)
            if edge_key in self.edge_labels:
                del self.edge_labels[edge_key]

    def edges_connected(self, node):
        return [edge for edge in self.edges if node in edge[:2]]

    def add_node(self, coords):
        self.nodes.append(coords)

    def delete_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        edge_key = self.edge_to_string(edge)
        if edge_key in self.edge_labels:
            del self.edge_labels[edge_key]

    def get_edge(self, node1, node2):
        # Get a ref to the existing edge, if it exists
        for edge in self.edges:
            if edge[:2] == (node1, node2) or edge[:2] == (node2, node1):
                return edge
        dist = self.calculate_distance(
            node1, node2
        )  # Calculate distance for every get_edge call
        # Sort nodes to treat edges as undirected
        if node1[0] > node2[0] or (node1[0] == node2[0] and node1[1] > node2[1]):
            return (node2, node1, dist)
        return (node1, node2, dist)

    def find_closest_node(self, coords):
        closest_node = None
        min_distance = float("inf")
        for node in self.nodes:
            distance = (node[0] - coords[0]) ** 2 + (node[1] - coords[1]) ** 2
            if distance < min_distance:
                closest_node = node
                min_distance = distance
        return closest_node, min_distance
