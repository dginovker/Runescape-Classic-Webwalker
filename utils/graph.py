import json
import os
from tkinter import messagebox, simpledialog


class Graph:
    def __init__(self):
        if not os.path.exists("graph.json"):
            self.nodes = []
            self.edges = []
            self.edge_labels = {}
        else:
            with open("graph.json", "r") as f:
                data = json.load(f)
                self.nodes = data["nodes"]
                self.edges = data["edges"]
                self.edge_labels = data.get("labels", {})

    def save(self):
        save_data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "labels": self.edge_labels,
        }
        with open("graph.json", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Save", "Graph saved successfully.")

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
        if messagebox.askyesno(
            "Delete Node", "Do you want to delete this node and its connected edges?"
        ):
            self.nodes.remove(node)
            # Remove connected edges and labels
            edges_to_remove = [edge for edge in self.edges if node in edge]
            for edge in edges_to_remove:
                self.edges.remove(edge)
                edge_key = self.edge_to_string(self.get_edge(edge[0], edge[1]))
                if edge_key in self.edge_labels:
                    del self.edge_labels[edge_key]

    def add_node(self, coords):
        self.nodes.append(coords)

    def delete_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        if self.edge_to_string(edge) in self.edge_labels:
            del self.edge_labels[self.edge_to_string(edge)]

    def get_edge(self, node1, node2):
        # Sort nodes to treat edges as undirected
        return sorted([node1, node2], key=lambda x: (x[0], x[1]))
    
    def edge_to_string(self, edge):
        return str(edge[0]) + "-" + str(edge[1])

    def find_closest_node(self, coords):
        closest_node = None
        min_distance = float("inf")
        for node in self.nodes:
            distance = (node[0] - coords[0]) ** 2 + (node[1] - coords[1]) ** 2
            if distance < min_distance:
                closest_node = node
                min_distance = distance
        return closest_node, min_distance
