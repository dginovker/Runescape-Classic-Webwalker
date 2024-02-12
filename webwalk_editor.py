import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import json
import os


class ImageEditor:
    def __init__(self, master, img_path):
        self.master = master
        self.original_img = Image.open(img_path)
        self.zoom_factor = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.update_coordinates)
        self.master.bind("<KeyPress>", self.on_key)
        self.label = tk.Label(master, text="Coordinates: (0, 370)")
        self.label.grid(row=0, column=1)
        self.save_button = tk.Button(master, text="Save", command=self.save_graph)
        self.save_button.grid(row=0, column=2)
        self.graph = {"nodes": [], "edges": []}
        self.load_graph()
        self.start_point = None
        self.redraw()

    def redraw(self):
        # Calculate the crop box based on the current offset and zoom factor
        x1 = self.offset_x
        y1 = self.offset_y
        x2 = x1 + int(400 / self.zoom_factor)
        y2 = y1 + int(400 / self.zoom_factor)
        cropped = self.original_img.crop((x1, y1, x2, y2))
        self.tk_img = ImageTk.PhotoImage(cropped.resize((400, 400), Image.LANCZOS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.draw_graph()

    def draw_graph(self):
        for node in self.graph["nodes"]:
            self.draw_node(node)
        for edge in self.graph["edges"]:
            self.draw_edge(edge)

    def draw_node(self, node):
        x, y = node
        x = (x - self.offset_x) * self.zoom_factor
        y = (y - self.offset_y + 370) * self.zoom_factor
        if 0 <= x <= 400 and 0 <= y <= 400:
            self.canvas.create_oval(
                x - 1.5, y - 1.5, x + 1.5, y + 1.5, fill="red", outline=""
            )

    def draw_edge(self, edge):
        start, end = edge
        start_x, start_y = (start[0] - self.offset_x) * self.zoom_factor, (
            start[1] - self.offset_y + 370
        ) * self.zoom_factor
        end_x, end_y = (end[0] - self.offset_x) * self.zoom_factor, (
            end[1] - self.offset_y + 370
        ) * self.zoom_factor
        if all(0 <= v <= 400 for v in [start_x, start_y, end_x, end_y]):
            self.canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=2)

    def on_click(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y - 370
        )
        coords = (int(x), int(y))
        if self.start_point:
            self.graph["edges"].append([self.start_point, coords])
            self.start_point = None
        else:
            self.start_point = coords
            self.graph["nodes"].append(coords)
        self.redraw()

    def update_coordinates(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y - 370
        )
        self.label.config(text=f"Coordinates: ({int(x)}, {int(y)})")

    def on_key(self, event):
        step = 30 / self.zoom_factor
        zoom_step = 0.1
        key = event.keysym
        if key in ["Right", "6"]:
            self.offset_x += step
        elif key in ["Left", "4"]:
            self.offset_x -= step
        elif key in ["Up", "8"]:
            self.offset_y -= step
        elif key in ["Down", "2"]:
            self.offset_y += step
        elif key in ["Plus", "Add", "KP_Add"]:
            self.zoom_factor = min(
                self.zoom_factor + zoom_step, 5.0
            )  # Limit zoom to prevent excessive zoom
        elif key in ["Minus", "Subtract", "KP_Subtract"]:
            self.zoom_factor = max(
                self.zoom_factor - zoom_step, 1.0
            )  # Prevent zooming out too much
        self.redraw()

    def save_graph(self):
        with open("graph.json", "w") as f:
            json.dump(self.graph, f)

    def load_graph(self):
        if os.path.exists("graph.json"):
            with open("graph.json", "r") as f:
                self.graph = json.load(f)


def main():
    root = tk.Tk()
    editor = ImageEditor(root, "./coleslaw_map.png")
    root.title("Image Editor")
    root.mainloop()


if __name__ == "__main__":
    main()
