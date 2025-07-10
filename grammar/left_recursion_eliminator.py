# grammar/left_recursion_eliminator.py
import copy

class LeftRecursionEliminator:
    """Handles elimination of direct and indirect left recursion."""
    
    def __init__(self):
        pass
    
    def eliminate_left_recursion(self, grammar):
        """
        Eliminates both direct and indirect left recursion from the grammar.
        Returns the grammar without left recursion.
        """
        no_left_recursion_grammar = copy.deepcopy(grammar)
        processed_rules = []
        
        for nt_A in list(no_left_recursion_grammar.keys()):
            # Handle indirect recursion
            for nt_B in processed_rules:
                # if a rule A -> Bγ exists, replace B with its productions
                productions_A = no_left_recursion_grammar[nt_A]
                new_productions_A = []
                for prod in productions_A:
                    if prod[0] == nt_B:
                        for prod_B in no_left_recursion_grammar[nt_B]:
                            new_productions_A.append(prod_B + prod[1:])
                    else:
                        new_productions_A.append(prod)
                no_left_recursion_grammar[nt_A] = new_productions_A

            # Handle direct recursion
            alphas, betas = [], [] # alphas for A -> Aα, betas for A -> β
            for prod in no_left_recursion_grammar[nt_A]:
                if prod[0] == nt_A:
                    alphas.append(prod[1:])
                else:
                    betas.append(prod)
            
            if alphas: # If direct left recursion found
                nt_A_prime = nt_A + "'" # Create new non-terminal (A')
                # A -> βA'
                no_left_recursion_grammar[nt_A] = [beta + [nt_A_prime] for beta in betas]
                # A' -> αA' | ε
                no_left_recursion_grammar[nt_A_prime] = [alpha + [nt_A_prime] for alpha in alphas] + [['ε']]

            processed_rules.append(nt_A) # Add A to processed list for next non-terminal

        
        return no_left_recursion_grammar 