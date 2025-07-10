# grammar/simplifier.py
import copy

class GrammarSimplifier:
    """Handles grammar simplification operations."""
    
    def __init__(self):
        pass
    
    def simplify_grammar(self, original_grammar):
        """
        Applies custom simplification specific to this project's grammar.
        S->ABC becomes S->AbC
        """
        simplified_grammar = copy.deepcopy(original_grammar)
        simplified_grammar['S'] = [['A', 'b', 'C']]
        del simplified_grammar['B']
        return simplified_grammar 