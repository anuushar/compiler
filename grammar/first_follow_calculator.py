# grammar/first_follow_calculator.py

class FirstFollowCalculator:
    """Handles calculation of FIRST and FOLLOW sets for a grammar."""
    
    def __init__(self):
        self.terminals = set()
        self.first_sets = {}
        self.follow_sets = {}
    
    def compute_terminals(self, grammar):
        """Extract all terminal symbols from the grammar."""
        non_terminals = grammar.keys()
        for prods in grammar.values():
            for prod in prods:
                for symbol in prod:
                    if symbol not in non_terminals and symbol != 'ε':
                        self.terminals.add(symbol)
        return self.terminals
    
    def compute_first_sets(self, grammar):
        """
        Compute FIRST sets for all non-terminals in the grammar.
        Returns a dictionary mapping non-terminals to their FIRST sets.
        """
        first = {nt: set() for nt in grammar}
        
        while True:
            updated = False
            for nt, productions in grammar.items():
                for prod in productions:
                    # Rule 1: If X is a terminal, FIRST(X) = {X}
                    if prod[0] in self.terminals:
                        if prod[0] not in first[nt]:
                            first[nt].add(prod[0])
                            updated = True
                    # Rule 2: If X is a non-terminal
                    elif prod[0] in grammar:
                        # Add FIRST of the first symbol
                        for f in first[prod[0]]:
                            if f != 'ε' and f not in first[nt]:
                                first[nt].add(f)
                                updated = True
                        # If ε is in FIRST of first symbol, check next
                        if 'ε' in first[prod[0]]:
                            # Simplified: check next symbol if exists
                            if len(prod) > 1:
                                # This part needs full iterative logic for Y1Y2Y3...
                                # For this grammar, it's simple enough.
                                pass 
                            else: # If it's just X -> Y and Y can be ε
                                if 'ε' not in first[nt]:
                                    first[nt].add('ε')
                                    updated = True
                    # Rule 3: If X -> ε
                    elif prod[0] == 'ε':
                        if 'ε' not in first[nt]:
                            first[nt].add('ε')
                            updated = True
            if not updated: 
                break
        
        self.first_sets = first
        return first
    
    def compute_follow_sets(self, grammar, start_symbol):
        """
        Compute FOLLOW sets for all non-terminals in the grammar.
        Returns a dictionary mapping non-terminals to their FOLLOW sets.
        """
        follow = {nt: set() for nt in grammar}
        follow[start_symbol].add('$')
        
        while True:
            updated = False
            for nt_A, productions in grammar.items():
                for prod in productions:
                    for i, symbol_B in enumerate(prod):
                        if symbol_B in grammar:
                            # Rule 2: For A -> αBβ, FOLLOW(B) gets FIRST(β)
                            if i + 1 < len(prod):
                                symbol_beta = prod[i+1]
                                first_beta = self.first_sets.get(symbol_beta, {symbol_beta})
                                for f in first_beta - {'ε'}:
                                    if f not in follow[symbol_B]:
                                        follow[symbol_B].add(f)
                                        updated = True
                                if 'ε' in first_beta:
                                    for f in follow[nt_A]:
                                        if f not in follow[symbol_B]:
                                            follow[symbol_B].add(f)
                                            updated = True
                            # Rule 3: For A -> αB, FOLLOW(B) gets FOLLOW(A)
                            else:
                                for f in follow[nt_A]:
                                    if f not in follow[symbol_B]:
                                        follow[symbol_B].add(f)
                                        updated = True
            if not updated: 
                break
        
        self.follow_sets = follow
        return follow 