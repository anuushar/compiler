# parser/predictive_parser.py
from syntax_parser.tree import TreeNode

class PredictiveParser:
    """Implements an LL(1) predictive parser."""

    def __init__(self, parsing_table, non_terminals, start_symbol):
        """
        Initializes the parser with pre-computed grammar data.
        """
        self.parsing_table = parsing_table
        self.non_terminals = set(non_terminals)
        # Terminals are derived from the parsing table keys, excluding the end marker.
        self.terminals = self._get_terminals_from_table()
        self.start_symbol = start_symbol
        self.end_marker = '$'
        self.parse_tree = None

    def _get_terminals_from_table(self):
        """
        Extracts terminal symbols from the parsing table keys.
        """
        terminals = set()
        for _, terminal in self.parsing_table.keys():
            terminals.add(terminal)
        return terminals - {'$'}
    
    def parse(self, input_string, step_callback=None, tree_callback=None):
        """
        Parses the input string using the LL(1) parsing algorithm.
        Optionally, calls callbacks for step-by-step logging and tree updates.
        """
        # Prepare input string and initialize parser stacks
        input_string = input_string + self.end_marker
        stack = [self.end_marker, self.start_symbol]
        
        # Initialize parse tree and its corresponding node stack
        self.parse_tree = TreeNode(self.start_symbol)
        tree_stack = [self.parse_tree]
        
        # Initialize parsing state variables
        index = 0
        step = 0
        result = None
        
        # Main parsing loop
        while stack:
            # Get current stack top and input lookahead
            top = stack[-1] 
            current_input = input_string[index] if index < len(input_string) else '$'
            
            # Prepare step information for callbacks
            step += 1
            stack_str = ''.join(reversed(stack))
            input_str = input_string[index:]
            action = ""

            # Rule 1: Acceptance condition (both stack and input consumed)
            if top == self.end_marker and top == current_input:
                action = "✓ Accepted: String parsed successfully"
                result = True
                if step_callback: step_callback(step, stack_str, input_str, action)
                break

            # Rule 2: If stack top is a terminal
            elif top in self.terminals:
                if top == current_input: # Match terminal with lookahead
                    action = f"Match: '{top}'"
                    stack.pop()
                    index += 1
                else: # Terminal mismatch error
                    action = f"✗ Error: Expected '{top}', found '{current_input}'"
                    result = False
                    if step_callback: step_callback(step, stack_str, input_str, action)
                    break
            
            # Rule 3: If stack top is a non-terminal
            elif top in self.non_terminals:
                key = (top, current_input) # Create lookup key for parsing table
                if key in self.parsing_table: # Check if a production rule exists
                    production = self.parsing_table[key]
                    action = f"Apply {top} → {''.join(production) if production != ['ε'] else 'ε'}"
                    
                    # Pop the non-terminal and its corresponding tree node
                    stack.pop()
                    current_tree_node = tree_stack.pop()

                    # Handle non-epsilon productions: add children to tree and push symbols to stacks
                    if production != ['ε']:
                        children_nodes = [TreeNode(s, s in self.terminals) for s in production]
                        for child in children_nodes:
                            current_tree_node.add_child(child)
                        
                        for i in range(len(production) - 1, -1, -1):
                            stack.append(production[i])
                            if production[i] in self.non_terminals:
                                tree_stack.append(children_nodes[i])
                    else: # Handle epsilon production: add an epsilon node to the tree
                        current_tree_node.add_child(TreeNode('ε', True))
                else: # Error: No production rule found for the given (non-terminal, lookahead)
                    action = f"✗ Error: No production for ({top}, {current_input})"
                    result = False
                    if step_callback: step_callback(step, stack_str, input_str, action)
                    break
            # Fallback for unexpected symbols on stack (should not happen in a valid setup)
            else:
                action = f"✗ Error: Invalid symbol '{top}' in stack"
                result = False
                if step_callback: step_callback(step, stack_str, input_str, action)
                break
            
            # Invoke callbacks if provided
            if step_callback: step_callback(step, stack_str, input_str, action)
            if tree_callback: tree_callback(self.parse_tree)
        
        return result # Return the final parsing result