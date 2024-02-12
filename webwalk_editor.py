import tkinter as tk
from tkinter import simpledialog, messagebox  # Import messagebox for confirmations
from PIL import Image, ImageTk
import json
import os

MAX_X_COORDINATE = 900  # The maximum value of X in the coordinate system


class ImageEditor:
    def __init__(self, master, img_path):
        self.master = master
        self.original_img = Image.open(img_path)
        self.zoom_factor = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.selected_node = None
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.update_coordinates)
        self.master.bind("<KeyPress>", self.on_key)
        self.label = tk.Label(master, text="Coordinates: (0, 0)")
        self.label.grid(row=0, column=1)
        self.save_button = tk.Button(master, text="Save", command=self.save_graph)
        self.save_button.grid(row=0, column=2)
        self.graph = {"nodes": [], "edges": []}
        self.edge_labels = {}
        self.load_graph()
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")  # Clear the canvas before redrawing
        x1 = self.offset_x
        y1 = self.offset_y
        x2 = x1 + int(400 / self.zoom_factor)
        y2 = y1 + int(400 / self.zoom_factor)
        cropped = self.original_img.crop((x1, y1, x2, y2))
        self.tk_img = ImageTk.PhotoImage(cropped.resize((400, 400), Image.LANCZOS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.draw_graph()
        if self.selected_node is not None:
            self.draw_node(self.selected_node, selected=True)

    def draw_graph(self):
        for node in self.graph["nodes"]:
            self.draw_node(node, selected=node == self.selected_node)
        for edge in self.graph["edges"]:
            self.draw_edge(edge)

    def draw_node(self, node, selected=False):
        x, y = node
        x = (x - self.offset_x) * self.zoom_factor
        y = (y - self.offset_y) * self.zoom_factor
        if 0 <= x <= 400 and 0 <= y <= 400:
            color = "green" if selected else "red"
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="")

    def draw_edge(self, edge):
        start, end = edge[0], edge[1]
        start_x, start_y = (
            (start[0] - self.offset_x) * self.zoom_factor,
            (start[1] - self.offset_y) * self.zoom_factor,
        )
        end_x, end_y = (
            (end[0] - self.offset_x) * self.zoom_factor,
            (end[1] - self.offset_y) * self.zoom_factor,
        )
        if all(0 <= v <= 400 for v in [start_x, start_y, end_x, end_y]):
            line = self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="red", width=2
            )
            edge_key = self.make_edge_key(edge[0], edge[1])
            if edge_key in self.edge_labels:
                self.canvas.create_text(
                    (start_x + end_x) / 2,
                    (start_y + end_y) / 2,
                    text=self.edge_labels[edge_key],
                    fill="blue",
                )

    def create_or_edit_edge(self, node_from, node_to, prompt_for_label=True):
        edge = [node_from, node_to]
        edge_reversed = [node_to, node_from]
        edge_key = self.make_edge_key(node_from, node_to)
        if edge not in self.graph["edges"] and edge_reversed not in self.graph["edges"]:
            self.graph["edges"].append(edge)
            return True
        elif prompt_for_label and edge_key in self.edge_labels:
            self.prompt_edge_label(edge)
        return False

    def prompt_edge_label(self, edge):
        edge_key = self.make_edge_key(edge[0], edge[1])
        existing_label = self.edge_labels.get(edge_key, "")
        label = simpledialog.askstring(
            "Label Edge",
            "Enter label for this edge:",
            initialvalue=existing_label,
            parent=self.master,
        )
        if label is not None:  # Check for Cancel click
            self.edge_labels[edge_key] = label
        else:
            if messagebox.askyesno("Delete Edge", "Do you want to delete this edge?"):
                self.delete_edge(edge)

    def delete_node(self, node):
        if messagebox.askyesno(
            "Delete Node", "Do you want to delete this node and its connected edges?"
        ):
            self.graph["nodes"].remove(node)
            # Remove connected edges and labels
            edges_to_remove = [edge for edge in self.graph["edges"] if node in edge]
            for edge in edges_to_remove:
                self.graph["edges"].remove(edge)
                edge_key = self.make_edge_key(edge[0], edge[1])
                if edge_key in self.edge_labels:
                    del self.edge_labels[edge_key]

            self.selected_node = None
            self.redraw()  # Ensure the canvas is updated immediately after deletion

    def on_click(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y
        )
        coords = (int(x), int(y))
        closest_node, distance = self.find_closest_node(coords)

        if distance <= 9:  # Click is within 3 tiles of an existing node
            if self.selected_node == closest_node:
                self.delete_node(closest_node)  # Delete node if it's the selected one
            elif self.selected_node and self.selected_node != closest_node:
                if not self.create_or_edit_edge(
                    self.selected_node, closest_node, prompt_for_label=False
                ):
                    self.prompt_edge_label([self.selected_node, closest_node])
                self.selected_node = closest_node  # Update selected node
            else:
                self.selected_node = closest_node
        else:
            self.graph["nodes"].append(coords)
            if self.selected_node:
                self.create_or_edit_edge(
                    self.selected_node, coords, prompt_for_label=False
                )
            self.selected_node = coords  # Automatically select the new node

        self.redraw()  # Redraw after any click action to ensure the canvas is up-to-date

    def delete_edge(self, edge):
        edge_key = self.make_edge_key(edge[0], edge[1])
        if edge in self.graph["edges"]:
            self.graph["edges"].remove(edge)
        elif [edge[1], edge[0]] in self.graph[
            "edges"
        ]:  # Remove reversed edge if present
            self.graph["edges"].remove([edge[1], edge[0]])
        if edge_key in self.edge_labels:
            del self.edge_labels[edge_key]
        self.redraw()

    def make_edge_key(self, node1, node2):
        # Sort nodes to treat edges as undirected
        sorted_nodes = sorted([node1, node2], key=lambda x: (x[0], x[1]))
        return str(sorted_nodes[0]) + "-" + str(sorted_nodes[1])

    def update_coordinates(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y
        )
        self.label.config(text=f"Coordinates: ({int(x)}, {int(y)})")

    def on_key(self, event):
        self.handle_navigation(event.keysym)

    def handle_navigation(self, key):
        step = 30 / self.zoom_factor
        zoom_step = 0.1
        if key in ["Right", "6"]:
            self.offset_x += step
        elif key in ["Left", "4"]:
            self.offset_x -= step
        elif key in ["Up", "8"]:
            self.offset_y -= step
        elif key in ["Down", "2"]:
            self.offset_y += step
        elif key in ["Plus", "Add", "KP_Add"]:
            self.zoom_factor = min(self.zoom_factor + zoom_step, 5.0)
        elif key in ["Minus", "Subtract", "KP_Subtract"]:
            self.zoom_factor = max(self.zoom_factor - zoom_step, 1.0)
        elif key in ["Escape", "space", "Return", "KP_Enter"]:
            self.selected_node = None
        self.redraw()

    def save_graph(self):
        save_data = {
            "nodes": self.graph["nodes"],
            "edges": self.graph["edges"],
            "labels": self.edge_labels,
        }
        with open("graph.json", "w") as f:
            json.dump(save_data, f)
        messagebox.showinfo("Save", "Graph saved successfully.")

    def load_graph(self):
        if os.path.exists("graph.json"):
            with open("graph.json", "r") as f:
                data = json.load(f)
                self.graph = {"nodes": data["nodes"], "edges": data["edges"]}
                self.edge_labels = data.get("labels", {})

    def find_closest_node(self, coords):
        closest_node = None
        min_distance = float("inf")
        for node in self.graph["nodes"]:
            distance = (node[0] - coords[0]) ** 2 + (node[1] - coords[1]) ** 2
            if distance < min_distance:
                closest_node = node
                min_distance = distance
        return closest_node, min_distance


def main():
    root = tk.Tk()
    editor = ImageEditor(root, "./map.png")
    root.title("Image Editor")
    root.mainloop()


if __name__ == "__main__":
    main()
