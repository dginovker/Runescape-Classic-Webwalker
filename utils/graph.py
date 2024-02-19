import os
from tkinter import messagebox, simpledialog


class Graph:
    def __init__(self):
        self.filename = "graph.txt"
        self.nodes = []
        self.edges = []
        self.edge_labels = {}
        if os.path.exists(self.filename):
            self.load()

    def save(self):
        with open(self.filename, "w") as f:
            for node in self.nodes:
                f.write(f"N:{node[0]},{node[1]}\n")
            for edge in self.edges:
                f.write(f"E:{edge[0][0]},{edge[0][1]},{edge[1][0]},{edge[1][1]}\n")
            for edge, label in self.edge_labels.items():
                node1, node2 = edge.split("-")
                f.write(f"L:{node1},{node2},{label}\n")
        messagebox.showinfo("Save", "Graph saved successfully.")

    def load(self):
        with open(self.filename, "r") as f:
            for line in f:
                if line.startswith("N:"):
                    parts = line[2:].strip().split(",")
                    self.nodes.append((int(parts[0]), int(parts[1])))
                elif line.startswith("E:"):
                    parts = line[2:].strip().split(",")
                    self.edges.append(
                        ((int(parts[0]), int(parts[1])), (int(parts[2]), int(parts[3])))
                    )
                elif line.startswith("L:"):
                    parts = line[2:].strip().split(",")
                    edge = (
                        (int(parts[0]), int(parts[1])),
                        (int(parts[2]), int(parts[3])),
                    )
                    self.edge_labels[self.edge_to_string(edge)] = parts[4]

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
        if node1[0] > node2[0]:
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
