# grammar/parsing_table_builder.py

class ParsingTableBuilder:
    """Handles construction of predictive parsing tables."""
    
    def __init__(self):
        pass
    
    def create_parsing_table(self, grammar, first_sets, follow_sets, terminals):
        """
        Builds a predictive parsing table from the grammar, FIRST sets, and FOLLOW sets.
        Returns a dictionary mapping (non_terminal, terminal) pairs to productions.
        """
        table = {}
        # 'E': [['T', "E'"]],    
        
        for nt_A, productions in grammar.items():
            #[['T', "E'"]]
            for prod in productions:
                first_of_prod = set()
                # Simplified calculation of FIRST(prod)
                if prod[0] in terminals:
                    first_of_prod.add(prod[0])
                elif prod[0] in grammar:
                    first_of_prod.update(first_sets[prod[0]])
                else: # Epsilon production
                    first_of_prod.add('ε')

                for terminal in first_of_prod - {'ε'}:
                    table[(nt_A, terminal)] = prod
                
                if 'ε' in first_of_prod:
                    for terminal in follow_sets[nt_A]:
                        table[(nt_A, terminal)] = prod
        
        return table 