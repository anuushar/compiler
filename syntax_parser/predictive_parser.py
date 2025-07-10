# parser/predictive_parser.py
from syntax_parser.tree import TreeNode

class PredictiveParser:
    def __init__(self, parsing_table, non_terminals, start_symbol):
        """
        Initializes the parser with a pre-computed parsing table.
        """
        self.parsing_table = parsing_table
        self.non_terminals = set(non_terminals)
        self.terminals = self._get_terminals_from_table()
        self.start_symbol = start_symbol
        self.end_marker = '$'
        self.parse_tree = None

    def _get_terminals_from_table(self):
        terminals = set()
        for _, terminal in self.parsing_table.keys():
            terminals.add(terminal)
        return terminals - {'$'}
    
    # The 'parse' method from the previous answer can be copied here.
    # It remains unchanged as its logic is independent of the grammar.
    def parse(self, input_string, step_callback=None, tree_callback=None):
        input_string = input_string + self.end_marker
        stack = [self.end_marker, self.start_symbol]
        
        self.parse_tree = TreeNode(self.start_symbol)
        tree_stack = [self.parse_tree]
        
        index = 0
        step = 0
        result = None
        
        while stack:
            top = stack[-1] 
            current_input = input_string[index] if index < len(input_string) else '$'
            
            step += 1
            stack_str = ''.join(reversed(stack))
            input_str = input_string[index:]
            action = ""

            if top == self.end_marker and top == current_input:
                action = "✓ Accepted: String parsed successfully"
                result = True
                if step_callback: step_callback(step, stack_str, input_str, action)
                break

            elif top in self.terminals:
                if top == current_input:
                    action = f"Match: '{top}'"
                    stack.pop()
                    index += 1
                else:
                    action = f"✗ Error: Expected '{top}', found '{current_input}'"
                    result = False
                    if step_callback: step_callback(step, stack_str, input_str, action)
                    break
            
            elif top in self.non_terminals:
                key = (top, current_input)
                if key in self.parsing_table:
                    production = self.parsing_table[key]
                    action = f"Apply {top} → {''.join(production) if production != ['ε'] else 'ε'}"
                    
                    stack.pop()
                    current_tree_node = tree_stack.pop()

                    if production != ['ε']:
                        # Add children to tree
                        children_nodes = [TreeNode(s, s in self.terminals) for s in production]
                        for child in children_nodes:
                            current_tree_node.add_child(child)
                        
                        # Push symbols to stacks in reverse
                        for i in range(len(production) - 1, -1, -1):
                            stack.append(production[i])
                            if production[i] in self.non_terminals:
                                tree_stack.append(children_nodes[i])
                    else:
                        current_tree_node.add_child(TreeNode('ε', True))
                else:
                    action = f"✗ Error: No production for ({top}, {current_input})"
                    result = False
                    if step_callback: step_callback(step, stack_str, input_str, action)
                    break
            else: # Should not happen with a correct grammar/table
                action = f"✗ Error: Invalid symbol '{top}' in stack"
                result = False
                if step_callback: step_callback(step, stack_str, input_str, action)
                break
            
            if step_callback: step_callback(step, stack_str, input_str, action)
            if tree_callback: tree_callback(self.parse_tree)
        
        return result