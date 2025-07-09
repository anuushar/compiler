import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
from parser.predictive_parser import PredictiveParser
from ui.tree_canvas import ParseTreeCanvas

class ParserApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Predictive Parser")
        self.geometry("1100x700")
        self.minsize(900, 600)
        # Nord-inspired color palette
        self.colors = {
            'background': '#2e3440',
            'card': '#3b4252',
            'primary': '#5e81ac',
            'accent': '#88c0d0',
            'success': '#a3be8c',
            'error': '#bf616a',
            'text': '#eceff4',
            'text_secondary': '#d8dee9',
            'border': '#4c566a',
        }
        self.fonts = {
            'heading': font.Font(family="Segoe UI", size=16, weight="bold"),
            'subheading': font.Font(family="Segoe UI", size=12, weight="bold"),
            'body': font.Font(family="Segoe UI", size=10),
            'code': font.Font(family="Consolas", size=10),
        }
        self.parser = PredictiveParser()
        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        self.configure(bg=self.colors['background'])
        # Title
        title = tk.Label(self, text="Predictive Parser", font=self.fonts['heading'],
                         bg=self.colors['background'], fg=self.colors['primary'])
        title.pack(pady=(18, 2))
        subtitle = tk.Label(self, text="Grammar:", font=self.fonts['subheading'],
                            bg=self.colors['background'], fg=self.colors['accent'])
        subtitle.pack()
        grammar = tk.Label(self, text="S  → A b E\nA  → ab A'\nA' → ab A' | ε\nE  → c E | ε",
                           font=self.fonts['code'], justify="left",
                           bg=self.colors['background'], fg=self.colors['text_secondary'])
        grammar.pack(pady=(0, 10))
        # Input frame
        input_frame = tk.Frame(self, bg=self.colors['background'])
        input_frame.pack(pady=(0, 10))
        tk.Label(input_frame, text="Input String:", font=self.fonts['body'],
                 bg=self.colors['background'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 8))
        self.input_entry = tk.Entry(input_frame, font=self.fonts['body'], width=30, bg=self.colors['card'], fg=self.colors['text'])
        self.input_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.input_entry.bind('<Return>', lambda e: self.on_parse())
        self.parse_btn = tk.Button(input_frame, text="Parse", font=self.fonts['subheading'],
                                   command=self.on_parse, bg=self.colors['primary'], fg=self.colors['text'],
                                   activebackground=self.colors['accent'], activeforeground=self.colors['background'])
        self.parse_btn.pack(side=tk.LEFT)
        # Main content frame
        content_frame = tk.Frame(self, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 10))
        # Parsing steps table
        table_card = tk.Frame(content_frame, bg=self.colors['card'], bd=1, relief=tk.RIDGE)
        table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        tk.Label(table_card, text="Parsing Steps", font=self.fonts['subheading'],
                 bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(10, 0))
        columns = ("Step", "Stack", "Input", "Action")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=90 if col != "Action" else 200)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background=self.colors['card'],
                        fieldbackground=self.colors['card'],
                        foreground=self.colors['text'],
                        rowheight=24,
                        bordercolor=self.colors['border'],
                        borderwidth=1)
        style.map('Treeview', background=[('selected', self.colors['accent'])])
        v_scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        # Parse tree canvas
        tree_card = tk.Frame(content_frame, bg=self.colors['card'], bd=1, relief=tk.RIDGE)
        tree_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        tk.Label(tree_card, text="Parse Tree", font=self.fonts['subheading'],
                 bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(10, 0))
        self.tree_canvas = ParseTreeCanvas(tree_card, bg=self.colors['background'])
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Result label
        self.result_label = tk.Label(self, text="", font=self.fonts['subheading'],
                                     bg=self.colors['background'], fg=self.colors['text'])
        self.result_label.pack(pady=(8, 0))

    def on_parse(self):
        self.tree.delete(*self.tree.get_children())
        self.result_label.config(text="", fg=self.colors['text'])
        input_str = self.input_entry.get().strip()
        if not input_str:
            self.result_label.config(text="Please enter a string to parse.", fg=self.colors['error'])
            return
        def step_callback(step, stack, input_, action):
            self.tree.insert("", "end", values=(step, stack, input_, action))
            self.tree.yview_moveto(1)
        def tree_callback(tree_root):
            self.tree_canvas.set_tree(tree_root)
        result = self.parser.parse(input_str, step_callback=step_callback, tree_callback=tree_callback)
        if result:
            self.result_label.config(text="Accepted", fg=self.colors['success'])
        else:
            self.result_label.config(text="Rejected", fg=self.colors['error']) 