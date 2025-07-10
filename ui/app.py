import tkinter as tk
from tkinter import ttk, font
from ui.tree_canvas import ParseTreeCanvas

class ParserApp(tk.Tk):
    def __init__(self, parser, analyzer):
        super().__init__()
        self.parser = parser
        self.analyzer = analyzer
        
        self.title("LL(1) Parser Generator & Analyzer")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # --- Nord Theme Setup ---
        self.colors = {
            'background': '#2e3440', 'card': '#3b4252', 'primary': '#5e81ac',
            'accent': '#88c0d0', 'success': '#a3be8c', 'error': '#bf616a',
            'text': '#eceff4', 'text_secondary': '#d8dee9', 'border': '#4c566a',
        }
        self.fonts = {
            'heading': font.Font(family="Segoe UI", size=16, weight="bold"),
            'subheading': font.Font(family="Segoe UI", size=12, weight="bold"),
            'body': font.Font(family="Segoe UI", size=10),
            'code': font.Font(family="Consolas", size=11),
        }
        self.configure(bg=self.colors['background'])
        self._configure_ttk_style()

        # --- Create Tabs ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.parser_tab = ttk.Frame(self.notebook, style='App.TFrame')
        self.transform_tab = ttk.Frame(self.notebook, style='App.TFrame')
        self.table_tab = ttk.Frame(self.notebook, style='App.TFrame')

        self.notebook.add(self.parser_tab, text='   Parser   ')
        self.notebook.add(self.transform_tab, text='   Grammar Transformation   ')
        self.notebook.add(self.table_tab, text='   FIRST/FOLLOW & Table   ')
        
        self._create_parser_widgets(self.parser_tab)
        self._create_transform_widgets(self.transform_tab)
        self._create_table_widgets(self.table_tab)

    def _configure_ttk_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        # General widget styles
        style.configure('.', background=self.colors['background'], foreground=self.colors['text'], font=self.fonts['body'])
        style.configure('TFrame', background=self.colors['background'])
        style.configure('App.TFrame', background=self.colors['card'], borderwidth=1, relief='solid', bordercolor=self.colors['border'])
        # Notebook tabs
        style.configure("TNotebook", background=self.colors['background'], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors['card'], foreground=self.colors['text_secondary'], padding=[10, 5], font=self.fonts['body'])
        style.map("TNotebook.Tab", background=[("selected", self.colors['primary'])], foreground=[("selected", self.colors['text'])])
        # Treeview (for steps and table)
        style.configure("Treeview", background=self.colors['card'], fieldbackground=self.colors['card'], foreground=self.colors['text'], rowheight=25, borderwidth=0)
        style.map('Treeview', background=[('selected', self.colors['primary'])])
        style.configure("Treeview.Heading", background=self.colors['border'], foreground=self.colors['text'], font=self.fonts['body'], relief='flat')
        # Paned Window
        style.configure('TPanedwindow', background=self.colors['border'])

    def _format_grammar(self, grammar_dict):
        lines = []
        for nt, productions in grammar_dict.items():
            prods_str = ' | '.join([' '.join(p) if p != ['ε'] else 'ε' for p in productions])
            lines.append(f"{nt.ljust(3)} →  {prods_str}")
        return '\n'.join(lines)

    def _create_transform_widgets(self, parent):
        # This function remains unchanged
        orig_frame = ttk.LabelFrame(parent, text=" 1. Original Grammar ", style='Card.TLabelframe')
        orig_frame.pack(fill='x', pady=10, padx=10, anchor='n')
        tk.Label(orig_frame, text=self._format_grammar(self.analyzer.original_grammar), justify='left', font=self.fonts['code'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=5, pady=5)
        
        simp_frame = ttk.LabelFrame(parent, text=" 2. Simplified Grammar (BC -> bC) ", style='Card.TLabelframe')
        simp_frame.pack(fill='x', pady=10, padx=10, anchor='n')
        tk.Label(simp_frame, text=self._format_grammar(self.analyzer.simplified_grammar), justify='left', font=self.fonts['code'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=5, pady=5)
        
        final_frame = ttk.LabelFrame(parent, text=" 3. Final LL(1) Grammar (After Transformations) ", style='Card.TLabelframe')
        final_frame.pack(fill='x', pady=10, padx=10, anchor='n')
        tk.Label(final_frame, text=self._format_grammar(self.analyzer.final_grammar), justify='left', font=self.fonts['code'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=5, pady=5)

    def _create_table_widgets(self, parent):
        # This function remains unchanged
        sets_frame = ttk.Frame(parent, style='App.TFrame')
        sets_frame.pack(fill='x', pady=10, padx=10)
        first_frame = ttk.LabelFrame(sets_frame, text=" FIRST Sets ", style='Card.TLabelframe')
        first_frame.pack(side='left', expand=True, fill='x', padx=(0, 5))
        first_text = '\n'.join([f"{nt.ljust(3)}: {{ {', '.join(sorted(list(s)))} }}" for nt, s in self.analyzer.first_sets.items()])
        tk.Label(first_frame, text=first_text, justify='left', font=self.fonts['code'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=5, pady=5)
        follow_frame = ttk.LabelFrame(sets_frame, text=" FOLLOW Sets ", style='Card.TLabelframe')
        follow_frame.pack(side='left', expand=True, fill='x', padx=(5, 0))
        follow_text = '\n'.join([f"{nt.ljust(3)}: {{ {', '.join(sorted(list(s)))} }}" for nt, s in self.analyzer.follow_sets.items()])
        tk.Label(follow_frame, text=follow_text, justify='left', font=self.fonts['code'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=5, pady=5)
        
        table_frame = ttk.LabelFrame(parent, text=" Predictive Parsing Table ", style='Card.TLabelframe')
        table_frame.pack(fill='both', expand=True, pady=10, padx=10)
        terminals = sorted(list(self.parser.terminals)) + ['$']
        columns = ["Non-Terminal"] + terminals
        table_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            table_tree.heading(col, text=col); table_tree.column(col, anchor='center', width=120, stretch=False)
        for nt in sorted(self.analyzer.final_grammar.keys()):
            row_data = [nt]
            for t in terminals:
                prod = self.analyzer.parsing_table.get((nt, t))
                if prod: row_data.append(f"{nt} → {''.join(prod)}")
                else: row_data.append("")
            table_tree.insert("", "end", values=row_data)
        table_tree.pack(fill='both', expand=True)

    def _create_parser_widgets(self, parent):
        top_frame = ttk.Frame(parent, style='App.TFrame')
        top_frame.pack(fill='x', pady=10, padx=10)
        
        tk.Label(top_frame, text="Input String:", font=self.fonts['body'], bg=self.colors['card'], fg=self.colors['text']).pack(side='left', padx=(0, 8))
        self.input_entry = tk.Entry(top_frame, font=self.fonts['body'], width=40, bg=self.colors['background'], fg=self.colors['text'], insertbackground=self.colors['text'], relief=tk.FLAT)
        self.input_entry.pack(side='left', padx=(0, 8), expand=True, fill='x')
        self.parse_btn = tk.Button(top_frame, text="Parse", font=self.fonts['body'], command=self.on_parse, bg=self.colors['primary'], fg=self.colors['text'], activebackground=self.colors['accent'], activeforeground=self.colors['background'], relief=tk.FLAT, padx=10)
        self.parse_btn.pack(side='left')
        
        self.result_label = tk.Label(parent, text="", font=self.fonts['subheading'], bg=self.colors['card'], fg=self.colors['text'])
        self.result_label.pack(pady=5, padx=10, fill='x')
        
        content_pane = ttk.PanedWindow(parent, orient='horizontal', style='TPanedwindow')
        content_pane.pack(fill='both', expand=True, pady=(5,10), padx=10)

        steps_frame = ttk.LabelFrame(content_pane, text=" Parsing Steps ", style='Card.TLabelframe')
        columns = ("Step", "Stack", "Input", "Action")
        self.steps_tree = ttk.Treeview(steps_frame, columns=columns, show="headings")
        self.steps_tree.pack(fill='both', expand=True)
        for col in columns: self.steps_tree.heading(col, text=col)
        self.steps_tree.column("Step", width=50, stretch=False); self.steps_tree.column("Stack", width=150); self.steps_tree.column("Input", width=150); self.steps_tree.column("Action", width=300)
        content_pane.add(steps_frame, weight=3)

        tree_view_frame = ttk.LabelFrame(content_pane, text=" Parse Tree ", style='Card.TLabelframe')
        self.tree_canvas = ParseTreeCanvas(tree_view_frame, bg=self.colors['background'])
        self.tree_canvas.pack(fill='both', expand=True)
        content_pane.add(tree_view_frame, weight=2)

    def on_parse(self):
        self.steps_tree.delete(*self.steps_tree.get_children())
        self.result_label.config(text="")
        self.tree_canvas.set_tree(None)
        
        input_str = self.input_entry.get().strip()
        if not input_str:
            self.result_label.config(text="Please enter a string to parse.", fg=self.colors['error'])
            return

        def step_callback(step, stack, input_val, action):
            self.steps_tree.insert("", "end", values=(step, stack, input_val, action))
            self.steps_tree.yview_moveto(1)
        
        result = self.parser.parse(input_str, step_callback=step_callback, tree_callback=self.tree_canvas.set_tree)
        
        if result: self.result_label.config(text="✓ Accepted", fg=self.colors['success'])
        else: self.result_label.config(text="✗ Rejected", fg=self.colors['error'])
