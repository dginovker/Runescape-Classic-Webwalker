import os
from tkinter import messagebox, simpledialog
import numpy as np
from collections import deque


class Graph:
    def __init__(self):
        self.filename = "graph.txt"
        self.walkable_tiles = self.load_walkable_tiles()
        self.nodes = []
        self.edges = []
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
                distance = self.calculate_distance(edge[0], edge[1])
                label = self.edge_labels.get(self.edge_to_string(edge), "")
                f.write(
                    f"{edge[0][0]},{edge[0][1]},{edge[1][0]},{edge[1][1]},{distance},{label}\n"
                )
        messagebox.showinfo("Save", "Graph saved successfully.")

    def load(self):
        with open(self.filename, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                node1 = (int(parts[0]), int(parts[1]))
                node2 = (int(parts[2]), int(parts[3]))
                # Ensure nodes for the current edge are added
                if node1 not in self.nodes:
                    self.nodes.append(node1)
                if node2 not in self.nodes:
                    self.nodes.append(node2)
                # Add edge
                self.edges.append((node1, node2))
                # Add label if exists
                label = parts[5] if len(parts) > 5 else ""
                if label:
                    self.edge_labels[self.edge_to_string((node1, node2))] = label

    def edge_to_string(self, edge):
        edge = self.get_edge(edge[0], edge[1])
        return f"{edge[0][0]},{edge[0][1]}-{edge[1][0]},{edge[1][1]}"

    def create_edge(self, node_from, node_to):
        edge = self.get_edge(node_from, node_to)
        if edge not in self.edges:
            self.edges.append(edge)

    def prompt_edge_label(self, edge, uimaster, redraw):
        existing_label = self.edge_labels.get(self.edge_to_string(edge), "")
        label = simpledialog.askstring(
            "Label Edge",
            "Enter label for this edge:",
            initialvalue=existing_label,
            parent=uimaster,
        )
        if label is not None:  # Check for Cancel click
            self.edge_labels[self.edge_to_string(edge)] = label
        else:
            if messagebox.askyesno("Delete Edge", "Do you want to delete this edge?"):
                self.delete_edge(edge)
                redraw()

    def delete_node(self, node):
        self.nodes.remove(node)
        # Remove connected edges and labels
        edges_to_remove = self.edges_connected(node)
        for edge in edges_to_remove:
            self.edges.remove(edge)
            edge_key = self.edge_to_string(self.get_edge(edge[0], edge[1]))
            if edge_key in self.edge_labels:
                del self.edge_labels[edge_key]

    def edges_connected(self, node):
        return [edge for edge in self.edges if node in edge]

    def add_node(self, coords):
        self.nodes.append(coords)

    def delete_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        if self.edge_to_string(edge) in self.edge_labels:
            del self.edge_labels[self.edge_to_string(edge)]

    def get_edge(self, node1, node2):
        # Sort nodes to treat edges as undirected
        if node1[0] > node2[0] or node1[0] == node2[0] and node1[1] > node2[1]:
            return (node2, node1)
        return (node1, node2)

    def find_closest_node(self, coords):
        closest_node = None
        min_distance = float("inf")
        for node in self.nodes:
            distance = (node[0] - coords[0]) ** 2 + (node[1] - coords[1]) ** 2
            if distance < min_distance:
                closest_node = node
                min_distance = distance
        return closest_node, min_distance
