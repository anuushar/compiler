from parser.tree import TreeNode

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