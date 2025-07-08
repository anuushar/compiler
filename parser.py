import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import time
from datetime import datetime

class TreeNode:
    def __init__(self, value, is_terminal=False):
        self.value = value
        self.is_terminal = is_terminal
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0

class PredictiveParser:
    def __init__(self):
        self.parsing_table = {
            ('S', 'a'): ['A', 'b', 'E'],
            ('A', 'a'): ['a', 'b', "A'"],
            ("A'", 'a'): ['a', 'b', "A'"],
            ("A'", 'b'): ['ε'],
            ('E', 'c'): ['c', 'E'],
            ('E', '$'): ['ε']
        }
        self.non_terminals = {'S', 'A', "A'", 'E'}
        self.terminals = {'a', 'b', 'c'}
        self.start_symbol = 'S'
        self.end_marker = '$'
        self.parse_tree = None

    def parse(self, input_string, step_callback=None, tree_callback=None):
        input_string = input_string + self.end_marker
        stack = [self.end_marker, self.start_symbol]
        
        # Initialize parse tree
        self.parse_tree = TreeNode(self.start_symbol)
        tree_stack = [self.parse_tree]
        
        index = 0
        step = 0
        result = None
        
        while stack:
            top = stack.pop()
            current_tree_node = tree_stack.pop() if tree_stack else None
            current_input = input_string[index] if index < len(input_string) else ''
            step += 1
            
            stack_str = ''.join(stack) + top if stack else top
            input_str = input_string[index:]
            action = ""
            
            if top == self.end_marker:
                if top == current_input:
                    action = "✓ Accepted: String parsed successfully"
                    if step_callback:
                        step_callback(step, stack_str, input_str, action)
                    result = True
                    break
                else:
                    action = f"✗ Error: Unexpected end of input"
                    if step_callback:
                        step_callback(step, stack_str, input_str, action)
                    result = False
                    break
            
            if top in self.non_terminals:
                key = (top, current_input)
                if key in self.parsing_table:
                    production = self.parsing_table[key]
                    action = f"Apply {top} → {''.join(production).replace('ε', 'ε')}"
                    
                    if production != ['ε']:
                        # Add children to tree
                        for symbol in production:
                            if symbol != 'ε':
                                child_node = TreeNode(symbol, symbol in self.terminals)
                                if current_tree_node:
                                    current_tree_node.add_child(child_node)
                        
                        # Add symbols to stack in reverse order
                        for symbol in reversed(production):
                            if symbol != 'ε':
                                stack.append(symbol)
                                if current_tree_node:
                                    tree_stack.append(current_tree_node.children[production.index(symbol)])
                    else:
                        # Epsilon production
                        if current_tree_node:
                            epsilon_node = TreeNode('ε', True)
                            current_tree_node.add_child(epsilon_node)
                else:
                    action = f"✗ Error: No production for ({top}, {current_input})"
                    if step_callback:
                        step_callback(step, stack_str, input_str, action)
                    result = False
                    break
            else:
                if top == current_input:
                    action = f"Match: '{top}'"
                    index += 1
                else:
                    action = f"✗ Error: Expected '{top}', found '{current_input}'"
                    if step_callback:
                        step_callback(step, stack_str, input_str, action)
                    result = False
                    break
            
            if step_callback:
                step_callback(step, stack_str, input_str, action)
            
            if tree_callback:
                tree_callback(self.parse_tree)
        
        return result

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

class ParserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Predictive Parser with Parse Tree")
        self.configure(bg="#f0f0f0")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Improved color scheme with better contrast
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'error': '#e74c3c',
            'warning': '#f39c12',
            'background': '#f0f0f0',
            'card': '#ffffff',
            'text': '#2c3e50',
            'text_light': '#34495e',
            'text_secondary': '#7f8c8d',
            'border': '#bdc3c7'
        }
        
        # Professional fonts
        self.fonts = {
            'heading': font.Font(family="Arial", size=16, weight="bold"),
            'subheading': font.Font(family="Arial", size=12, weight="bold"),
            'body': font.Font(family="Arial", size=10),
            'code': font.Font(family="Courier", size=10),
            'small': font.Font(family="Arial", size=9)
        }
        
        self.parser = PredictiveParser()
        self.parsing_history = []
        self.current_step = 0
        self.parsing_steps = []
        self.is_parsing = False
        
        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset Tree View", command=self.reset_tree_view)
        view_menu.add_command(label="Fit Tree to Window", command=self.fit_tree_to_window)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Grammar Help", command=self.show_grammar_help)

    def create_header(self):
        header_frame = tk.Frame(self, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame, 
            text="Predictive Parser with Parse Tree Visualization",
            font=self.fonts['heading'],
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(expand=True, anchor='center')

    def create_main_content(self):
        # Create main container with notebook for tabs
        main_frame = tk.Frame(self, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Parser tab
        self.create_parser_tab()
        
        # Tree tab
        self.create_tree_tab()
        
        # History tab
        self.create_history_tab()

    def create_parser_tab(self):
        parser_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(parser_frame, text="Parser")
        
        # Grammar section
        self.create_grammar_section(parser_frame)
        
        # Input section
        self.create_input_section(parser_frame)
        
        # Parsing table
        self.create_parsing_table(parser_frame)
        
        # Result section
        self.create_result_section(parser_frame)

    def create_tree_tab(self):
        tree_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(tree_frame, text="Parse Tree")
        
        # Tree controls
        controls_frame = tk.Frame(tree_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(controls_frame, text="Parse Tree Visualization", font=self.fonts['subheading'],
                bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        button_frame = tk.Frame(controls_frame, bg=self.colors['card'])
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Reset View", command=self.reset_tree_view,
                 bg=self.colors['secondary'], fg='white', font=self.fonts['body']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Fit to Window", command=self.fit_tree_to_window,
                 bg=self.colors['secondary'], fg='white', font=self.fonts['body']).pack(side=tk.LEFT, padx=5)
        
        # Tree legend
        legend_frame = tk.Frame(controls_frame, bg=self.colors['card'])
        legend_frame.pack(pady=10)
        
        tk.Label(legend_frame, text="Legend:", font=self.fonts['body'], 
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        # Legend items
        legend_items = [
            ("Non-terminal", "#3498db"),
            ("Terminal", "#27ae60"),
            ("Epsilon (ε)", "#f39c12")
        ]
        
        for text, color in legend_items:
            item_frame = tk.Frame(legend_frame, bg=self.colors['card'])
            item_frame.pack(side=tk.LEFT, padx=10)
            
            tk.Label(item_frame, text="●", fg=color, font=("Arial", 16), 
                    bg=self.colors['card']).pack(side=tk.LEFT)
            tk.Label(item_frame, text=text, font=self.fonts['small'], 
                    bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(5, 0))
        
        # Tree canvas
        canvas_frame = tk.Frame(tree_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.tree_canvas = ParseTreeCanvas(canvas_frame, bg='white')
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_history_tab(self):
        history_frame = tk.Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(history_frame, text="History")
        
        # History controls
        controls_frame = tk.Frame(history_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(controls_frame, text="Parsing History", font=self.fonts['subheading'],
                bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        button_frame = tk.Frame(controls_frame, bg=self.colors['card'])
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Clear History", command=self.clear_history,
                 bg=self.colors['error'], fg='white', font=self.fonts['body']).pack(side=tk.LEFT, padx=5)
        
        # History table
        history_table_frame = tk.Frame(history_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        history_table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        columns = ("Timestamp", "Input", "Result", "Steps")
        self.history_tree = ttk.Treeview(history_table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, anchor=tk.CENTER, width=200)
        
        history_scrollbar = ttk.Scrollbar(history_table_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def create_grammar_section(self, parent):
        grammar_frame = tk.Frame(parent, bg=self.colors['background'])
        grammar_frame.pack(fill=tk.X, pady=(0, 20))
        
        card = tk.Frame(grammar_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)
        
        title = tk.Label(card, text="Grammar Rules", font=self.fonts['subheading'],
                        bg=self.colors['card'], fg=self.colors['text'])
        title.pack(pady=(15, 5))
        
        grammar_text = "S  → A b E\nA  → ab A'\nA' → ab A' | ε\nE  → c E | ε"
        grammar_label = tk.Label(card, text=grammar_text, font=self.fonts['code'],
                                bg=self.colors['card'], fg=self.colors['text_light'], justify=tk.LEFT)
        grammar_label.pack(pady=(0, 15))

    def create_input_section(self, parent):
        input_frame = tk.Frame(parent, bg=self.colors['background'])
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        card = tk.Frame(input_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)
        
        controls = tk.Frame(card, bg=self.colors['card'])
        controls.pack(pady=20)
        
        tk.Label(controls, text="Input String:", font=self.fonts['body'],
                bg=self.colors['card'], fg=self.colors['text']).grid(row=0, column=0, padx=(0, 10), sticky='w')
        
        self.input_entry = tk.Entry(controls, font=self.fonts['body'], width=30, relief=tk.SUNKEN, bd=2)
        self.input_entry.grid(row=0, column=1, padx=(0, 15), ipady=5)
        self.input_entry.bind('<Return>', lambda e: self.on_parse())
        
        self.parse_btn = tk.Button(controls, text="Parse", font=self.fonts['body'], command=self.on_parse,
                                  bg=self.colors['secondary'], fg='black', relief=tk.RAISED, bd=2,
                                  padx=20, pady=5, cursor='hand2')
        self.parse_btn.grid(row=0, column=2, padx=(0, 10))
        
        tk.Button(controls, text="Clear", font=self.fonts['body'], command=self.clear_all,
                 bg=self.colors['text_secondary'], fg='black', relief=tk.RAISED, bd=2,
                 padx=20, pady=5, cursor='hand2').grid(row=0, column=3, padx=(0, 10))

    def create_parsing_table(self, parent):
        table_frame = tk.Frame(parent, bg=self.colors['background'])
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        card = tk.Frame(table_frame, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        title = tk.Label(card, text="Parsing Steps", font=self.fonts['subheading'],
                        bg=self.colors['card'], fg=self.colors['text'])
        title.pack(pady=(15, 10))
        
        tree_frame = tk.Frame(card, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        columns = ("Step", "Stack", "Input", "Action")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        column_widths = {"Step": 80, "Stack": 150, "Input": 200, "Action": 400}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=column_widths[col])
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    def create_result_section(self, parent):
        result_frame = tk.Frame(parent, bg=self.colors['background'])
        result_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.result_label = tk.Label(result_frame, text="", font=self.fonts['subheading'],
                                    bg=self.colors['background'], fg=self.colors['text'])
        self.result_label.pack(pady=10)

    def create_widgets(self):
        self.create_menu()
        self.create_header()
        self.create_main_content()

    def clear_all(self):
        self.input_entry.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.result_label.config(text="", fg=self.colors['text'])
        self.tree_canvas.set_tree(None)

    def on_parse(self):
        if self.is_parsing:
            return
        
        self.tree.delete(*self.tree.get_children())
        self.result_label.config(text="", fg=self.colors['text'])
        
        input_str = self.input_entry.get().strip()
        
        if not input_str:
            messagebox.showwarning("Input Required", "Please enter a string to parse.")
            return
        
        self.is_parsing = True
        self.parse_btn.config(state='disabled', text='Parsing...')
        self.parsing_steps = []
        
        def step_callback(step, stack, input_, action):
            self.parsing_steps.append((step, stack, input_, action))
            self.add_step_instant(step, stack, input_, action)
        
        def tree_callback(tree_root):
            self.tree_canvas.set_tree(tree_root)
        
        result = self.parser.parse(input_str, step_callback=step_callback, tree_callback=tree_callback)
        
        # Update result
        if result:
            self.result_label.config(text="✓ ACCEPTED", fg=self.colors['success'])
            result_text = "ACCEPTED"
        else:
            self.result_label.config(text="✗ REJECTED", fg=self.colors['error'])
            result_text = "REJECTED"
        
        # Add to history
        self.add_to_history(input_str, result_text, len(self.parsing_steps))
        
        # Show final tree
        self.tree_canvas.set_tree(self.parser.parse_tree)
        
        self.is_parsing = False
        self.parse_btn.config(state='normal', text='Parse')

    def add_step_instant(self, step, stack, input_, action):
        if action.startswith('✓'):
            tags = ('success',)
        elif action.startswith('✗'):
            tags = ('error',)
        elif action.startswith('Match'):
            tags = ('match',)
        else:
            tags = ('normal',)
        
        self.tree.insert("", "end", values=(step, stack, input_, action), tags=tags)
        
        # Configure row colors
        self.tree.tag_configure('success', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('error', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('match', background='#cce5ff', foreground='#004085')
        self.tree.tag_configure('normal', background='white', foreground='#2c3e50')

    def add_to_history(self, input_str, result, steps):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.parsing_history.append({
            'timestamp': timestamp,
            'input': input_str,
            'result': result,
            'steps': steps
        })
        
        self.history_tree.insert("", "end", values=(timestamp, input_str, result, steps))

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all parsing history?"):
            self.parsing_history.clear()
            self.history_tree.delete(*self.history_tree.get_children())

    def reset_tree_view(self):
        self.tree_canvas.scale_factor = 1.0
        self.tree_canvas.pan_x = 0
        self.tree_canvas.pan_y = 0
        self.tree_canvas.draw_tree()

    def fit_tree_to_window(self):
        # Simple fit to window implementation
        self.tree_canvas.scale_factor = 0.8
        self.tree_canvas.pan_x = 50
        self.tree_canvas.pan_y = 50
        self.tree_canvas.draw_tree()

    def show_about(self):
        about_text = """Predictive Parser v1.0

Features:
• Interactive parse tree visualization
• Comprehensive parsing history
• Professional UI with modern design

Grammar:
S  → A b E
A  → ab A'
A' → ab A' | ε
E  → c E | ε

Controls:
• Click and drag to pan the tree view
• Use mouse wheel to zoom in/out

Developed with Python and Tkinter"""
        
        messagebox.showinfo("About", about_text)

    def show_grammar_help(self):
        help_text = """Grammar Help

Current Grammar Rules:
S  → A b E
A  → ab A'
A' → ab A' | ε
E  → c E | ε

Valid Input Examples:
• "abc" - Simple valid string
• "ababc" - String with A' recursion
• "abccc" - String with E recursion
• "ab" - String ending with epsilon in E
• "ababccc" - Complex valid string

Invalid Input Examples:
• "ac" - Missing 'b' between A and E
• "ba" - Wrong order of terminals
• "abcc" - Invalid based on grammar rules

Parsing Process:
1. Input string is processed left-to-right
2. Stack-based predictive parsing is used
3. Parse tree is built during parsing
4. Each step shows stack state and actions taken

Tree Legend:
• Blue circles: Non-terminal symbols
• Green circles: Terminal symbols
• Orange circles: Epsilon (ε) productions"""
        
        messagebox.showinfo("Grammar Help", help_text)

def main():
    app = ParserApp()
    app.mainloop()

if __name__ == "__main__":
    main()