import tkinter as tk
from parser.tree import TreeNode

class ParseTreeCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tree_root = None
        self.node_radius = 25
        self.level_height = 80
        self.node_spacing = 60
        self.colors = {
            'non_terminal': '#3498db',
            'terminal': '#27ae60',
            'epsilon': '#f39c12',
            'text': 'white',
            'line': '#2c3e50'
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
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.draw_tree()

    def on_zoom(self, event):
        if event.delta > 0 or event.num == 4:
            self.scale_factor *= 1.1
        else:
            self.scale_factor *= 0.9
        self.draw_tree()

    def set_tree(self, tree_root):
        self.tree_root = tree_root
        if tree_root:
            self.calculate_positions(tree_root)
            self.draw_tree()

    def calculate_positions(self, node, level=0, position=0):
        if not node:
            return 0
        
        node.y = level * self.level_height + 50
        
        if node.is_leaf():
            node.x = position * self.node_spacing + 100
            return position + 1
        
        # Calculate positions for children
        child_positions = []
        current_pos = position
        
        for child in node.children:
            current_pos = self.calculate_positions(child, level + 1, current_pos)
            child_positions.append(child.x)
        
        # Center parent over children
        if child_positions:
            node.x = (min(child_positions) + max(child_positions)) / 2
        else:
            node.x = position * self.node_spacing + 100
        
        return current_pos

    def draw_tree(self):
        self.delete("all")
        if not self.tree_root:
            return
        
        self.draw_node(self.tree_root)

    def draw_node(self, node):
        if not node:
            return
        
        # Apply transformations
        x = node.x * self.scale_factor + self.pan_x
        y = node.y * self.scale_factor + self.pan_y
        radius = self.node_radius * self.scale_factor
        
        # Draw connections to children
        for child in node.children:
            child_x = child.x * self.scale_factor + self.pan_x
            child_y = child.y * self.scale_factor + self.pan_y
            self.create_line(x, y, child_x, child_y, fill=self.colors['line'], width=2)
        
        # Choose color based on node type
        if node.value == 'ε':
            color = self.colors['epsilon']
        elif node.is_terminal:
            color = self.colors['terminal']
        else:
            color = self.colors['non_terminal']
        
        # Draw node
        self.create_oval(x - radius, y - radius, x + radius, y + radius, 
                        fill=color, outline=self.colors['line'], width=2)
        
        # Draw text
        self.create_text(x, y, text=node.value, fill=self.colors['text'], 
                        font=('Arial', int(12 * self.scale_factor), 'bold'))
        
        # Draw children
        for child in node.children:
            self.draw_node(child) 