import tkinter as tk
from PIL import Image
from utils.graph import Graph
from utils.draw import Drawer


class ImageEditor:
    def __init__(self, master, img_path):
        self.master = master
        self.original_img = Image.open(img_path)
        self.zoom_factor = 1.0
        self.offset_x, self.offset_y = 0, 0
        self.selected_node = None

        self.graph = Graph()
        self.drawer = Drawer(self)
        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.drawer.update_coordinates)
        self.master.bind("<KeyPress>", self.on_key)
        self.label = tk.Label(master, text="Coordinates: (0, 0)")
        self.label.grid(row=0, column=1)
        self.save_button = tk.Button(master, text="Save", command=self.graph.save)
        self.save_button.grid(row=0, column=2)
        self.drawer.redraw()

        # Undo functionality
        self.actions_history = []

    def add_action(self, action):
        self.actions_history.append(action)

    def undo(self):
        if not self.actions_history:
            return
        action = self.actions_history.pop()
        action_type, data = action

        if action_type == 'add_node':
            self.graph.delete_node(data, False)
            self.selected_node = None
        elif action_type == 'delete_node':
            self.graph.add_node(data['coords'])
            for edge in data['edges']:
                self.graph.create_edge(edge[0], edge[1])
        elif action_type == 'add_edge':
            self.graph.delete_edge(data)
        elif action_type == 'delete_edge':
            self.graph.create_edge(data[0], data[1])

        self.drawer.redraw()

    def on_click(self, event):
        x, y = (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y
        )
        coords = (int(x), int(y))
        closest_node, distance = self.graph.find_closest_node(coords)

        if distance <= 9:  # Click is within 3 tiles of an existing node
            if not self.selected_node:
                self.selected_node = closest_node
            elif self.selected_node == closest_node:
                # Capture delete node action for undo
                self.add_action(('delete_node', {'coords': closest_node, 'edges': self.graph.edges_connected(closest_node)}))
                self.graph.delete_node(closest_node, True)
                self.selected_node = None
                self.drawer.redraw()
            elif self.graph.get_edge(self.selected_node, closest_node) not in self.graph.edges:
                # Capture add edge action for undo
                self.add_action(('add_edge', (self.selected_node, closest_node)))
                self.graph.create_edge(self.selected_node, closest_node)
                self.selected_node = closest_node
            else:
                # Add edge label
                self.graph.prompt_edge_label(
                    self.graph.get_edge(self.selected_node, closest_node),
                    self.master,
                    self.drawer.redraw,
                )
                self.selected_node = closest_node
        else:
            # Capture add node action for undo
            self.add_action(('add_node', coords))
            self.graph.add_node(coords)
            if self.selected_node:
                self.graph.create_edge(self.selected_node, coords)
            self.selected_node = coords

        self.drawer.redraw()

    def on_key(self, event):
        if event.keysym == 'z' and (event.state & 0x0004):  # CTRL+Z
            self.undo()
        else:
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
        self.drawer.redraw()


def main():
    root = tk.Tk()
    ImageEditor(root, "./map.png")
    root.title("RSC Webwalk Editor")
    root.mainloop()


if __name__ == "__main__":
    main()
