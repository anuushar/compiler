#interactive
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
        self.start_symbol = 'S'
        self.end_marker = '$'
    
    def parse(self, input_string):
        input_string = input_string + self.end_marker
        stack = [self.end_marker, self.start_symbol]
        index = 0
        step = 0
        
        # Print table header
        print("\nParsing Steps is given below:")
        print(f"{'Step':<5} | {'Stack':<20} | {'Input':<20} | {'Action':<30}")
        print("-" * 70)
        
        while stack:
            top = stack.pop()
            current_input = input_string[index] if index < len(input_string) else ''
            
            # Record current state before processing
            step += 1
            stack_str = ''.join(stack) + top if stack else top
            input_str = input_string[index:]
            action = ""
            
            if top == self.end_marker:
                if top == current_input:
                    action = "Accepted: String parsed successfully"
                    print(f"{step:<5} | {stack_str:<20} | {input_str:<20} | {action:<30}")
                    return True
                else:
                    action = f"Error: Unexpected end of input"
                    print(f"{step:<5} | {stack_str:<20} | {input_str:<20} | {action:<30}")
                    return False
            
            if top in self.non_terminals:
                key = (top, current_input)
                if key in self.parsing_table:
                    production = self.parsing_table[key]
                    action = f"Apply {top} → {''.join(production).replace('ε', 'ε')}"
                    
                    if production != ['ε']:
                        # Push in reverse order
                        for symbol in reversed(production):
                            if symbol != 'ε':
                                stack.append(symbol)
                else:
                    action = f"Error: No production for ({top}, {current_input})"
                    print(f"{step:<5} | {stack_str:<20} | {input_str:<20} | {action:<30}")
                    return False
            else:
                if top == current_input:
                    action = f"Match: '{top}'"
                    index += 1
                else:
                    action = f"Error: Expected '{top}', found '{current_input}'"
                    print(f"{step:<5} | {stack_str:<20} | {input_str:<20} | {action:<30}")
                    return False
            
            # Print current step
            print(f"{step:<5} | {stack_str:<20} | {input_str:<20} | {action:<30}")
        
        return False

def main():
    parser = PredictiveParser()
    print("Non-recursive Predictive Parser for Grammar:")
    print("S  → A b E")
    print("A  → ab A'")
    print("A' → ab A' | ε")
    print("E  → c E | ε")
    
    input_string = input("\nEnter a string to parse: ")
    result = parser.parse(input_string)
    print("\nResult:", "Accepted" if result else "Rejected")

if __name__ == "__main__":
    main()

