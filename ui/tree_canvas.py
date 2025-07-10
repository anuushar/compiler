import tkinter as tk
from syntax_parser.tree import TreeNode

class ParseTreeCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tree_root = None
        self.node_radius = 25
        self.level_height = 80
        self.node_spacing = 60
        self.colors = {
            'non_terminal': '#1976d2', # blue
            'terminal': '#43a047',    # green
            'epsilon': '#fbc02d',     # orange
            'text': '#111111',        # black for text
            'line': '#888888'         # dark gray for lines
        }
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<MouseWheel>', self.on_zoom)
        self.bind('<Button-4>', self.on_zoom)
        self.bind('<Button-5>', self.on_zoom)
        
        self.scale_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

    def on_click(self, event):
        self.drag_start_x = self.canvasx(event.x)
        self.drag_start_y = self.canvasy(event.y)

    def on_drag(self, event):
        dx = self.canvasx(event.x) - self.drag_start_x
        dy = self.canvasy(event.y) - self.drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self.drag_start_x = self.canvasx(event.x)
        self.drag_start_y = self.canvasy(event.y)
        self.draw_tree()

    def on_zoom(self, event):
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 4 or event.delta > 0:
            self.scale_factor *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.scale_factor *= 0.9
        self.draw_tree()

    def set_tree(self, tree_root):
        self.tree_root = tree_root
        if tree_root:
            # Reset view before drawing a new tree
            self.scale_factor = 1.0
            self.pan_x = self.winfo_width() / 4 # Initial centering
            self.pan_y = 50
            self.calculate_positions(self.tree_root)
            self.draw_tree()
        else:
            self.delete("all")

    def calculate_positions(self, node, level=0, position=0):
        if not node:
            return 0
        
        node.y = level * self.level_height
        
        if node.is_leaf():
            node.x = position * self.node_spacing
            return position + 1
        
        # Calculate positions for children first
        child_positions_x = []
        current_pos = position
        for child in node.children:
            current_pos = self.calculate_positions(child, level + 1, current_pos)
            child_positions_x.append(child.x)
        
        # Center parent over its children
        if child_positions_x:
            node.x = (min(child_positions_x) + max(child_positions_x)) / 2
        else:
            node.x = position * self.node_spacing
        
        return current_pos

    def draw_tree(self):
        self.delete("all")
        if not self.tree_root:
            return
        
        self.draw_node(self.tree_root)

    def draw_node(self, node):
        if not node or not hasattr(node, 'x'):
            return
        
        # Apply transformations for pan and zoom
        x = node.x * self.scale_factor + self.pan_x
        y = node.y * self.scale_factor + self.pan_y
        radius = self.node_radius * self.scale_factor
        
        # Draw connections to children first (so they are layered below the nodes)
        for child in node.children:
            if hasattr(child, 'x'):
                child_x = child.x * self.scale_factor + self.pan_x
                child_y = child.y * self.scale_factor + self.pan_y
                self.create_line(x, y, child_x, child_y, fill=self.colors['line'], width=max(1, 2 * self.scale_factor))
        
        # Recursively draw children nodes
        for child in node.children:
            self.draw_node(child)

        # Choose color based on node type from your color scheme
        if node.value == 'ε':
            color = self.colors['epsilon']
        elif node.is_terminal:
            color = self.colors['terminal']
        else:
            color = self.colors['non_terminal']
        
        # Draw the node oval and its text
        self.create_oval(x - radius, y - radius, x + radius, y + radius, 
                           fill=color, outline=self.colors['line'], width=max(1, 2 * self.scale_factor))
        
        font_size = max(6, int(12 * self.scale_factor))
        self.create_text(x, y, text=node.value, fill=self.colors['text'], 
                           font=('Segoe UI', font_size, 'bold'))
