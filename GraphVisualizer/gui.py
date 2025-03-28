import tkinter as tk
from edge import Edge
from node import Node
from graph import Graph
import math
import random
from tkinter import messagebox


def random_color():
    """Generate a random color."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"


class GraphGUI:
    def __init__(self, graph, root=None):
        self.graph = graph
        self.root = root if root else tk.Tk()
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack()

        self.directed_var = tk.BooleanVar()  # Directed checkbox
        self.undirected_var = tk.BooleanVar()  # Undirected checkbox

        self.directed_checkbox = tk.Checkbutton(self.root, text="Directed Graph", variable=self.directed_var,
                                                command=self.makeDirected)
        self.directed_checkbox.pack(side=tk.LEFT, padx=5)

        self.undirected_checkbox = tk.Checkbutton(self.root, text="Undirected Graph", variable=self.undirected_var,
                                                  command=self.makeUndirected)
        self.undirected_checkbox.pack(side=tk.LEFT, padx=5)

        # Set default state
        self.directed_var.set(True)
        self.undirected_var.set(False)
        self.graph.directed = True

        self.selected_node = None
        self.selected_nodes = []  # To store the two selected nodes
        self.node_radius = 20
        self.edges = {}
        self.nodes = {}
        self.node_counter = 1
        self.mouse_drag_data = {"x": 0, "y": 0}  # mouse drag

        self.canvas.bind("<Button-2>", self.on_canvas_click)  # Middle click for selection
        self.canvas.bind("<B2-Motion>", self.on_canvas_drag)  # Middle click drag for movement
        self.canvas.bind("<ButtonRelease-2>", self.on_canvas_release)  # Stop dragging on release

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # Right-click to delete edge

        # Algorithm selection menu
        self.algorithm_var = tk.StringVar(value="BFS")
        self.algorithm_menu = tk.OptionMenu(self.root, self.algorithm_var, "BFS", "DFS", "Recursive DFS")
        self.algorithm_menu.pack(side=tk.LEFT, padx=5)

        # Run button
        self.run_button = tk.Button(self.root, text="Run", command=self.run_algorithm)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.color_button = tk.Button(self.root, text="Connected Components", command=self.color_connected_components)
        self.color_button.pack(side=tk.LEFT, padx=5)

        self.color_button = tk.Button(self.root, text="Strongly Connected Components", command=self.color_scc)
        self.color_button.pack(side=tk.LEFT, padx=5)

        self.color_button = tk.Button(self.root, text="Topological Sort", command=self.color_topological_sort)
        self.color_button.pack(side=tk.LEFT, padx=2)

        self.check_button = tk.Button(self.root, text="Check Tree", command=self.check_tree_button)
        self.check_button.pack(side=tk.RIGHT, padx=5)

        # Bind spacebar to clear canvas function
        self.root.bind("<space>", self.clear_canvas)
        self.root.bind("<KeyPress-d>", self.delete_selected_node)
        self.root.bind("<KeyPress-f>", self.color_center)
        self.root.bind("<KeyPress-t>", self.display_tree)

        self.root.title("Graph Visualizer")

    def run(self):
        """Run the Tkinter event loop."""
        self.root.mainloop()

    def makeDirected(self):
        """Set the graph type to directed."""
        self.graph.directed = True
        self.undirected_var.set(False)  # Uncheck the undirected checkbox
        self.draw_graph()

    def makeUndirected(self):
        """Set the graph type to undirected."""
        self.graph.directed = False
        self.directed_var.set(False)  # Uncheck the directed checkbox
        self.draw_graph()

    def draw_graph(self):
        """Redraw the entire graph."""
        self.canvas.delete("all")

        # Draw nodes
        for node in self.graph.nodes:
            node_obj = self.nodes.get(node)
            self.draw_node(node_obj)

        # Draw edges
        for edge in self.edges.values():
            self.draw_edge(edge)

    def draw_node(self, node):
        """Draw a node on the canvas and store its IDs."""
        circle_id = self.canvas.create_oval(
            node.x - self.node_radius, node.y - self.node_radius,
            node.x + self.node_radius, node.y + self.node_radius,
            fill="lightblue", outline="black", width=2
        )
        text_id = self.canvas.create_text(node.x, node.y, text=node.id.split('_')[-1], font=("Arial", 12))

        # Assign these IDs to the node object for future reference
        node.circle_id = circle_id
        node.text_id = text_id

    def draw_edge(self, edge):
        """Draw an edge between two nodes."""
        # Get the coordinates of the start and end nodes
        x1, y1 = edge.start_node.x, edge.start_node.y
        x2, y2 = edge.end_node.x, edge.end_node.y

        # Calculate the distance between the nodes
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # If the nodes are the same (distance is zero), return without drawing the edge
        if distance == 0:
            return

        # Calculate the unit vector (direction) from the start node to the end node
        unit_dx = dx / distance
        unit_dy = dy / distance

        # Set the node radius
        node_radius = 20  # Adjust this as needed

        # Adjust the endpoints of the lines to stop at the outer edge of the nodes
        x1_end = x1 + unit_dx * node_radius
        y1_end = y1 + unit_dy * node_radius
        x2_end = x2 - unit_dx * node_radius
        y2_end = y2 - unit_dy * node_radius

        # Draw the line (edge) between the nodes, using arrow for directed edges
        if self.graph.directed:
            line_id = self.canvas.create_line(
                x1_end, y1_end, x2_end, y2_end,
                fill="black", width=2, arrow=tk.LAST
            )
        else:
            line_id = self.canvas.create_line(
                x1_end, y1_end, x2_end, y2_end,
                fill="black", width=2
            )

        # Assign the line ID to the edge for future reference
        edge.line_id = line_id

    def on_canvas_click(self, event):
        """Handle canvas click to add nodes or create edges."""
        clicked_node = self.get_clicked_node(event.x, event.y)

        if clicked_node:
            self.unhighlight_node()
            if self.selected_node is None:
                self.selected_node = clicked_node
                self.highlight_node(clicked_node)
                self.mouse_drag_data["x"] = event.x  # Store initial mouse position
                self.mouse_drag_data["y"] = event.y
            else:
                self.create_edge(self.selected_node, clicked_node)
                self.selected_node = None
        else:
            # Create a new node on click
            new_node_id = f"node_{self.node_counter}"
            new_node = Node(
                node_id=new_node_id,
                x=event.x,
                y=event.y,
                circle_id=None,
                text_id=None,
            )
            self.graph.add_node(new_node_id)
            self.nodes[new_node_id] = new_node
            self.draw_node(new_node)  # Ensure the node is drawn with IDs assigned
            self.node_counter += 1

    def get_clicked_node(self, x, y):
        """Return the node clicked on the canvas."""
        for node in self.nodes.values():
            if self.is_within_node(x, y, node):
                return node
        return None

    def on_canvas_drag(self, event):
        """Handle dragging a node when the middle mouse button is pressed."""
        if self.selected_node:
            # Calculate distance moved from initial mouse position
            delta_x = event.x - self.mouse_drag_data["x"]
            delta_y = event.y - self.mouse_drag_data["y"]

            # Move the selected node
            self.canvas.move(self.selected_node.circle_id, delta_x, delta_y)
            self.canvas.move(self.selected_node.text_id, delta_x, delta_y)

            # Update the node's position in the graph
            self.selected_node.x += delta_x
            self.selected_node.y += delta_y

            # Update the mouse drag data
            self.mouse_drag_data["x"] = event.x
            self.mouse_drag_data["y"] = event.y

            # Update edges connected to the node
            self.update_edges(self.selected_node)

    def on_canvas_release(self, event):
        """Stop dragging when the middle mouse button is released."""
        self.selected_node = None  # Deselect node after dragging ends

    def update_edges(self, node):
        """Update edges after dragging a node."""
        for edge in self.edges.values():
            if edge.start_node == node or edge.end_node == node:
                self.canvas.coords(edge.line_id,
                                   edge.start_node.x, edge.start_node.y,
                                   edge.end_node.x, edge.end_node.y)

    def is_within_node(self, x, y, node):
        """Check if the click is within the bounds of a node."""
        return (node.x - self.node_radius <= x <= node.x + self.node_radius and
                node.y - self.node_radius <= y <= node.y + self.node_radius)

    def highlight_node(self, node):
        """Highlight the selected node by changing its fill color to yellow."""
        self.canvas.itemconfig(node.circle_id, fill="yellow")

    def unhighlight_node(self):
        """Restore the original color of all nodes."""
        for node in self.nodes.values():
            self.canvas.itemconfig(node.circle_id, fill="lightblue")

    def create_edge(self, start_node, end_node):
        """Create an edge between two nodes."""
        edge_id = f"edge_{start_node.id}_{end_node.id}"
        new_edge = Edge(start_node, end_node, edge_id)
        self.edges[edge_id] = new_edge
        self.graph.add_edge(start_node.id, end_node.id)
        self.draw_graph()

    def on_canvas_right_click(self, event):
        """Handle right-click to delete edge between two nodes."""
        clicked_node = self.get_clicked_node(event.x, event.y)

        if clicked_node:
            if len(self.selected_nodes) == 0:
                self.selected_nodes.append(clicked_node)  # First node selected
                self.highlight_node(clicked_node)
            elif len(self.selected_nodes) == 1:
                self.selected_nodes.append(clicked_node)  # Second node selected
                self.delete_edge_between_nodes()
                self.selected_nodes = []  # Reset selection
                self.unhighlight_node()  # Remove highlights

    def delete_edge_between_nodes(self):
        """Delete the edge between two selected nodes."""
        node1, node2 = self.selected_nodes

        if self.graph.directed:
            edge_id = f"edge_{node1.id}_{node2.id}"
            if edge_id in self.edges:
                del self.edges[edge_id]
                self.graph.delete_edge(node1.id, node2.id)
                self.draw_graph()

        else:
            edge_id1 = f"edge_{node1.id}_{node2.id}"
            edge_id2 = f"edge_{node2.id}_{node1.id}"

            if edge_id1 in self.edges:
                del self.edges[edge_id1]
                self.graph.delete_edge(node1.id, node2.id)
            elif edge_id2 in self.edges:
                del self.edges[edge_id2]
                self.graph.delete_edge(node2.id, node1.id)

            self.draw_graph()

    def run_algorithm(self):
        """Run the selected algorithm starting from the selected node."""
        if self.selected_node is None:
            return  # No node selected, exit

        algorithm = self.algorithm_var.get()
        visited = set()
        order = []
        if algorithm == "BFS":
            order = self.graph.bfs(self.selected_node.id)
            self.highlight_nodes(order)
        elif algorithm == "DFS":
            order = self.graph.dfs(self.selected_node.id)
            self.highlight_nodes(order)
        elif algorithm == "Recursive DFS":
            self.graph.recursive_dfs(self.selected_node.id, visited, order)
            self.highlight_nodes(order)
        self.unhighlight_node()
        self.selected_node = None

    def highlight_nodes(self, order):
        """Highlight nodes in the given order."""
        for node_id in order:
            node = self.nodes[node_id]  # Get the node object
            self.unhighlight_node()  # Clear previous highlights
            self.highlight_node(node)  # Highlight the current node
            self.canvas.update()  # Update the canvas to show the highlight
            self.canvas.after(1000)  # Wait for 1 second before moving to the next node
        self.unhighlight_node()  # Clear highlights after traversal

    def clear_canvas(self, event=None):
        """Clear the canvas and reset all variables."""
        self.edges.clear()  # Clear the edges dictionary
        self.nodes.clear()  # Clear the nodes dictionary
        self.graph.nodes.clear()  # Clear the nodes in the graph object
        self.graph.adjacency_list.clear()  # Clear the adjacency list in the graph object
        self.node_counter = 1  # Reset node counter
        self.selected_node = None  # Clear the selected node
        self.selected_nodes = []  # Reset selected nodes
        self.canvas.delete("all")  # Clear the canvas

    def delete_selected_node(self, event):
        """Delete a selected node along with its connected edges."""
        if self.selected_node is not None:
            node_id = self.selected_node.id
            # Remove all edges connected to the node
            edges_to_remove = [
                edge_id for edge_id, edge in self.edges.items()
                if edge.start_node.id == node_id or edge.end_node.id == node_id
            ]
            for edge_id in edges_to_remove:
                edge = self.edges[edge_id]
                # Delete the graphical representation of the edge
                self.canvas.delete(edge.line_id)
                # Remove the edge from the edge dictionary
                del self.edges[edge_id]
                # Delete the edge from the graph structure
                self.graph.delete_edge(edge.start_node.id, edge.end_node.id)
            # Delete the node from the canvas
            self.canvas.delete(self.selected_node.circle_id)
            self.canvas.delete(self.selected_node.text_id)
            # Remove the node from the nodes dictionary and the graph object
            del self.nodes[node_id]
            self.graph.delete_node(node_id)
            # Clear the selected node
            self.selected_node = None
            # Redraw the graph to reflect changes
            self.draw_graph()

    def color_connected_components(self):
        """Color each connected component in a different color."""
        # First, find the connected components
        connected_components = self.graph.find_connected_components()

        # List of predefined colors (or you can generate random colors)
        colors = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "cyan"]

        # If there are more connected components than colors, extend the list
        if len(connected_components) > len(colors):
            while len(colors) < len(connected_components):
                colors.append(random_color())  # Add random colors if needed

        # Now, color the nodes in each connected component
        for idx, component in enumerate(connected_components):
            color = colors[idx]  # Get the color for this component
            for node_id in component:
                node = self.nodes.get(node_id)
                if node:
                    # Ensure all nodes in the connected component are assigned the same color
                    self.canvas.itemconfig(node.circle_id, fill=color)  # Color the node's circle

    def color_scc(self):
        strong_components = self.graph.kosaraju()
        colors = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "cyan"]
        if len(strong_components) > len(colors):
            while len(colors) < len(strong_components):
                colors.append(random_color())  # Add random colors if needed
        for idx, scc in enumerate(strong_components):
            color = colors[idx]  # Get the color for this SCC
            for node_id in scc:
                node = self.nodes.get(node_id)
                if node:
                    self.canvas.itemconfig(node.circle_id, fill=color)  # Color the node's circle

    def color_topological_sort(self):
        topological_order = self.graph.topological_sort()
        self.highlight_nodes(topological_order)

    def check_tree_button(self):
        is_tree_result = self.graph.is_tree()
        print(f"Result from is_tree(): {is_tree_result}")
        if is_tree_result:
            messagebox.showinfo("Result", "The graph is a tree.")
        else:
            messagebox.showinfo("Result", "The graph is not a tree.")

    def color_center(self, event=None):
        centers = self.graph.find_tree_center()
        for center_id in centers:
            center_node = self.nodes.get(center_id)
            if center_node:
                self.canvas.itemconfig(center_node.circle_id, fill="red")
        self.canvas.after(2000, self.unhighlight_node)

    def display_tree(self, event=None):
        centers = self.graph.find_tree_center()
        if not centers:
            messagebox.showerror("Error", "The graph is not a tree.")
            return
        tree_window = tk.Toplevel(self.root)
        tree_window.title("Tree Visualization")
        canvas = tk.Canvas(tree_window, width=800, height=600, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)
        adjacency_list = self.graph.adjacency_list

        def build_hierarchy(node_id, parent=None):
            if node_id not in adjacency_list:
                return {"id": node_id, "children": []}  # Safeguard for missing keys

            children = [n for n in adjacency_list.get(node_id, []) if n != parent]
            return {
                "id": node_id,
                "children": [build_hierarchy(child, node_id) for child in children]
            }

        tree_hierarchy = build_hierarchy(centers[0])
        positions = {}

        def calculate_positions(tree, x, y, level_width, level_height):
            node_id = tree["id"]
            positions[node_id] = (x,y)
            num_children = len(tree["children"])
            if num_children == 0:
                return
            child_x_start = x - (num_children - 1) * level_width // 2
            for idx, child in enumerate(tree["children"]):
                child_x = child_x_start + idx * level_width
                child_y = y + level_height
                calculate_positions(child, child_x, child_y, level_width, level_height)

        calculate_positions(tree_hierarchy, 400, 50, 100, 100)

        def draw_tree(tree):
            node_id = tree["id"]
            x, y = positions[node_id]
            circle_id = canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill="lightblue", outline="black", width=2
            )
            text_id = canvas.create_text(x, y, text=node_id.split('_')[-1], font=("Arial", 12))
            for child in tree["children"]:
                child_id = child["id"]
                child_x, child_y = positions[child_id]
                dx = child_x - x
                dy = child_y - y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance == 0:
                    continue
                unit_dx = dx / distance
                unit_dy = dy / distance
                x1_end = x + unit_dx * self.node_radius
                y1_end = y + unit_dy * self.node_radius
                x2_end = child_x - unit_dx * self.node_radius
                y2_end = child_y - unit_dy * self.node_radius
                canvas.create_line(
                    x1_end, y1_end, x2_end, y2_end,
                    fill="black", width=2, arrow=tk.LAST
                )
                draw_tree(child)

        draw_tree(tree_hierarchy)
