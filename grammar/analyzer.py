# grammar/analyzer.py
import copy
from grammar.simplifier import GrammarSimplifier
from grammar.left_recursion_eliminator import LeftRecursionEliminator
from grammar.left_factoring import LeftFactoring
from grammar.first_follow_calculator import FirstFollowCalculator
from grammar.parsing_table_builder import ParsingTableBuilder

class GrammarAnalyzer:
    def __init__(self, grammar_rules):
        self.original_grammar = copy.deepcopy(grammar_rules)
        self.start_symbol = list(grammar_rules.keys())[0]
        
        # Initialize the specialized components
        self.simplifier = GrammarSimplifier()
        self.recursion_eliminator = LeftRecursionEliminator()
        self.left_factoring = LeftFactoring()
        self.first_follow_calculator = FirstFollowCalculator()
        self.table_builder = ParsingTableBuilder()
        
        # --- Variables to store the results of each step ---
        self.simplified_grammar = {}
        self.no_left_recursion_grammar = {}
        self.final_grammar = {} # After left-factoring
        self.first_sets = {}
        self.follow_sets = {}
        self.parsing_table = {}
        self.terminals = set()

    def run_full_analysis(self):
        """Runs all the transformation and calculation steps in order."""
        # Step 1: A custom simplification specific to this project's grammar
        self.simplified_grammar = self.simplifier.simplify_grammar(self.original_grammar)
        
        # Step 2: Eliminate direct and indirect left recursion
        self.no_left_recursion_grammar = self.recursion_eliminator.eliminate_left_recursion(self.simplified_grammar)
        
        # Step 3: Eliminate common prefixes
        self.final_grammar = self.left_factoring.left_factor(self.no_left_recursion_grammar)

        # Step 4: Compute Terminals, FIRST sets, and FOLLOW sets
        self.terminals = self.first_follow_calculator.compute_terminals(self.final_grammar)
        self.first_sets = self.first_follow_calculator.compute_first_sets(self.final_grammar)
        self.follow_sets = self.first_follow_calculator.compute_follow_sets(self.final_grammar, self.start_symbol)

        # Step 5: Build the final parsing table
        self.parsing_table = self.table_builder.create_parsing_table(
            self.final_grammar, 
            self.first_sets, 
            self.follow_sets, 
            self.terminals
        )