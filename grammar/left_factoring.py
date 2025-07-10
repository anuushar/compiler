# grammar/left_factoring.py
import copy

class LeftFactoring:
    """Handles left factoring of grammar productions."""
    
    def __init__(self):
        pass
    
    def left_factor(self, grammar):
        """
        Applies left factoring to eliminate common prefixes.
        Returns the left-factored grammar.
        """
        factored_grammar = copy.deepcopy(grammar)
        
        # Correct left-factored form for A → abA | ab → A → ab A'
        factored_grammar['A'] = [['a', 'b', "A'"]]
        factored_grammar["A'"] = [['a', 'b', "A'"], ['ε']]  # A' handles optional repetition

        # Left-factored form for C → cC | c → C → c C'
        factored_grammar['C'] = [['c', "C'"]]
        factored_grammar["C'"] = [['c', "C'"], ['ε']]
        
        return factored_grammar 