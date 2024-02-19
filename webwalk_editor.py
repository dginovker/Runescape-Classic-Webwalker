import tkinter as tk
from PIL import Image
from utils.graph import Graph
from utils.draw import Drawer


class ImageEditor:
    def __init__(self, master, img_path):
        self.master = master
        self.original_img = Image.open(img_path)
        self.zoom_factor = 4.0
        self.offset_x, self.offset_y = 600, 450
        self.selected_node = None

        self.graph = Graph()
        self.drawer = Drawer(self)
        self.canvas = tk.Canvas(master, width=750, height=750)
        self.canvas.grid(row=1, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click_start)
        self.canvas.bind("<ButtonRelease-1>", self.on_click_end)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.master.bind("<KeyPress>", self.on_key)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows scroll
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down
        self.label = tk.Label(master, text="Coordinates: (0, 0)")
        self.label.grid(row=0, column=1)
        self.save_button = tk.Button(master, text="Save", command=self.graph.save)
        self.save_button.grid(row=0, column=2)
        self.drawer.redraw()

        # Undo functionality
        self.actions_history = []
        self.dragging = False  # To differentiate dragging from clicking
        self.drag_start_x = None
        self.drag_start_y = None

    def on_mousewheel(self, event):
        # Zoom in or out
        zoom_speed = 0.1  # Adjust zoom speed as needed
        if event.delta > 0 or event.num == 4:  # Scroll up or Linux scroll up
            self.zoom_factor = min(self.zoom_factor + zoom_speed, 20.0)
        elif event.delta < 0 or event.num == 5:  # Scroll down or Linux scroll down
            self.zoom_factor = max(
                self.zoom_factor - zoom_speed, 0.1
            )  # Prevent zooming out too much
        self.drawer.redraw()

    def on_click_start(self, event):
        self.drag_start_x, self.drag_start_y = event.x, event.y

    def on_motion(self, event):
        self.drawer.update_coordinates(event)

    def on_drag(self, event):
        if not self.drag_start_x or not self.drag_start_y:
            return
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        distance = (
            dx**2 + dy**2
        ) ** 0.5  # Calculate distance using Pythagorean theorem

        # Only proceed with dragging if the distance is >= 10 pixels
        if distance >= 10:
            self.offset_x -= dx / self.zoom_factor
            self.offset_y -= dy / self.zoom_factor
            self.drag_start_x, self.drag_start_y = event.x, event.y
            if not self.dragging:  # Set dragging flag only if moved more than 10 pixels
                self.dragging = True
                self.canvas.config(cursor="fleur")  # Change cursor to indicate dragging
            self.drawer.redraw()

    def on_click_end(self, event):
        # Calculate the distance moved to determine if it was a drag or click
        if self.drag_start_x is not None and self.drag_start_y is not None:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            distance = (dx**2 + dy**2) ** 0.5

            # Consider it a click only if the distance moved is less than 10 pixels
            if not self.dragging or distance < 10:
                self.on_click(event)

        # Reset the dragging state and cursor after the action is complete
        self.dragging = False
        self.canvas.config(cursor="")  # Revert cursor
        self.drag_start_x = None  # Reset drag start positions
        self.drag_start_y = None

    def on_click(self, event):
        if self.dragging:  # Skip node placement if dragging occurred
            return

        x, y = 900 - (event.x / self.zoom_factor + self.offset_x), (
            event.y / self.zoom_factor + self.offset_y
        )
        coords = (int(x), int(y))
        closest_node, distance = self.graph.find_closest_node(coords)

        if distance <= 5 * 3:  # Click is within 5 tiles of an existing node
            if not self.selected_node:
                self.selected_node = closest_node
            elif self.selected_node == closest_node:
                self.selected_node = None
            elif (
                self.graph.get_edge(self.selected_node, closest_node)
                not in self.graph.edges
            ):
                # Capture add edge action for undo
                self.actions_history.append(
                    ("add_edge", (self.selected_node, closest_node))
                )
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
            if self.graph.walkable_tiles[coords[0]][coords[1]] == 0:
                self.label.config(text=f"!  !  !   Tile {coords} isn't walkable   !  !  !")
                return
            # Capture add node action for undo
            self.actions_history.append(("add_node", coords))
            self.graph.add_node(coords)
            if self.selected_node:
                self.graph.create_edge(self.selected_node, coords)
            self.selected_node = coords

        self.drawer.redraw()

    def delete_node(self, node):
        if not node:
            return
        # Capture delete node action for undo
        self.actions_history.append(
            (
                "delete_node",
                {
                    "coords": node,
                    "edges": self.graph.edges_connected(node),
                },
            )
        )
        self.graph.delete_node(node)
        self.selected_node = None
        self.drawer.redraw()

    def on_key(self, event):
        if event.keysym == "z" and (event.state & 0x0004):  # CTRL+Z
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
        elif key in ["BackSpace", "Delete"]:
            self.delete_node(self.selected_node)
        self.drawer.redraw()

    def undo(self):
        if not self.actions_history:
            return
        action_type, data = self.actions_history.pop()

        if action_type == "add_node":
            self.graph.delete_node(data)
            self.selected_node = None
        elif action_type == "delete_node":
            self.graph.add_node(data["coords"])
            for edge in data["edges"]:
                self.graph.create_edge(edge[0], edge[1])
        elif action_type == "add_edge":
            self.graph.delete_edge(self.graph.get_edge(data[0], data[1]))
        elif action_type == "delete_edge":
            self.graph.create_edge(data[0], data[1])

        self.drawer.redraw()


def main():
    root = tk.Tk()
    ImageEditor(root, "./map.png")
    root.title("RSC Webwalk Editor")
    root.mainloop()


if __name__ == "__main__":
    main()
