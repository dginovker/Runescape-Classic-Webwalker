import tkinter as tk
from PIL import Image, ImageTk
from utils.graph import Graph

class ImageEditor:
    def __init__(self, master, img_path):
        self.master = master
        self.original_img = Image.open(img_path)
        self.zoom_factor = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.selected_node = None
        self.graph = Graph()
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.update_coordinates)
        self.master.bind("<KeyPress>", self.on_key)
        self.label = tk.Label(master, text="Coordinates: (0, 0)")
        self.label.grid(row=0, column=1)
        self.save_button = tk.Button(master, text="Save", command=self.graph.save)
        self.save_button.grid(row=0, column=2)
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
        for node in self.graph.nodes:
            self.draw_node(node, selected=node == self.selected_node)
        for edge in self.graph.edges:
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
            self.canvas.create_line(start_x, start_y, end_x, end_y, fill="red", width=2)
            edge_key = self.graph.make_edge_key(edge[0], edge[1])
            if edge_key in self.graph.edge_labels:
                self.canvas.create_text(
                    (start_x + end_x) / 2,
                    (start_y + end_y) / 2,
                    text=self.graph.edge_labels[edge_key],
                    fill="blue",
                )

    def on_click(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y
        )
        coords = (int(x), int(y))
        closest_node, distance = self.graph.find_closest_node(coords)

        if distance <= 9:  # Click is within 3 tiles of an existing node
            if not self.selected_node:
                self.selected_node = closest_node
            if self.selected_node == closest_node:
                self.graph.delete_node(
                    closest_node
                )  # Delete node if it's the selected one
                self.selected_node = None
                self.redraw()  # Ensure the canvas is updated immediately after deletion
            elif (
                self.graph.make_edge_key(self.selected_node, closest_node)
                not in self.graph.edge_labels
            ):
                # Create an edge
                self.graph.create_edge(self.selected_node, closest_node)
                self.selected_node = closest_node
            else:
                # Add edge label
                self.graph.prompt_edge_label(
                    [self.selected_node, closest_node], self.master, self.redraw
                )
                self.selected_node = closest_node
        else:
            self.graph.add_node(coords)
            if self.selected_node:
                self.graph.create_edge(self.selected_node, coords)
            self.selected_node = coords  # Automatically select the new node

        self.redraw()  # Redraw after any click action to ensure the canvas is up-to-date

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


def main():
    root = tk.Tk()
    ImageEditor(root, "./map.png")
    root.title("RSC Webwalk Editor")
    root.mainloop()


if __name__ == "__main__":
    main()
