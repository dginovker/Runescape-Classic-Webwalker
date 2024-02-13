"""
Drawing utils because I'm too lazy to keep looking at them in the webwalk_editor.py file.
"""

from PIL import Image, ImageTk
import tkinter as tk


class Drawer:
    def __init__(self, image_editor):
        self.image_editor = image_editor

    def redraw(self):
        self.image_editor.canvas.delete("all")  # Clear the canvas before redrawing
        x1 = self.image_editor.offset_x
        y1 = self.image_editor.offset_y
        x2 = x1 + int(400 / self.image_editor.zoom_factor)
        y2 = y1 + int(400 / self.image_editor.zoom_factor)
        cropped = self.image_editor.original_img.crop((x1, y1, x2, y2))
        self.image_editor.tk_img = ImageTk.PhotoImage(
            cropped.resize((400, 400), Image.LANCZOS)
        )
        self.image_editor.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.image_editor.tk_img
        )
        self.draw_graph()
        if self.image_editor.selected_node is not None:
            self.draw_node(self.image_editor.selected_node, selected=True)

    def draw_graph(self):
        for node in self.image_editor.graph.nodes:
            self.draw_node(node, selected=node == self.image_editor.selected_node)
        for edge in self.image_editor.graph.edges:
            self.draw_edge(edge)

    def draw_node(self, node, selected=False):
        x, y = node
        x = (x - self.image_editor.offset_x) * self.image_editor.zoom_factor
        y = (y - self.image_editor.offset_y) * self.image_editor.zoom_factor
        if 0 <= x <= 400 and 0 <= y <= 400:
            color = "green" if selected else "red"
            self.image_editor.canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5, fill=color, outline=""
            )

    def draw_edge(self, edge):
        start, end = edge[0], edge[1]
        start_x, start_y = (
            (start[0] - self.image_editor.offset_x) * self.image_editor.zoom_factor,
            (start[1] - self.image_editor.offset_y) * self.image_editor.zoom_factor,
        )
        end_x, end_y = (
            (end[0] - self.image_editor.offset_x) * self.image_editor.zoom_factor,
            (end[1] - self.image_editor.offset_y) * self.image_editor.zoom_factor,
        )
        if all(0 <= v <= 400 for v in [start_x, start_y, end_x, end_y]):
            self.image_editor.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="red", width=2
            )
            edge_key = self.image_editor.graph.edge_to_string(
                self.image_editor.graph.get_edge(edge[0], edge[1])
            )
            if edge_key in self.image_editor.graph.edge_labels:
                self.image_editor.canvas.create_text(
                    (start_x + end_x) / 2,
                    (start_y + end_y) / 2,
                    text=self.image_editor.graph.edge_labels[edge_key],
                    fill="blue",
                )

    def update_coordinates(self, event):
        x, y = (event.x / self.image_editor.zoom_factor + self.image_editor.offset_x), (
            event.y / self.image_editor.zoom_factor + self.image_editor.offset_y
        )
        self.image_editor.label.config(text=f"Coordinates: ({int(x)}, {int(y)})")
