# main.py
import tkinter as tk
from grammar.analyzer import GrammarAnalyzer
from syntax_parser.predictive_parser import PredictiveParser
from ui.app import ParserApp

def main():
    """
    Main function to orchestrate the parser generation and UI launch.
    """
    # Define the original grammar from the project requirements
    original_grammar = {
        'S': [['A', 'B', 'C']],
        'A': [['a', 'b', 'A'], ['a', 'b']],
        'B': [['b'], ['B', 'C']],
        'C': [['c'], ['c', 'C']]
    }

    # 1. Analyze the grammar to produce the parsing table and transformation steps
    analyzer = GrammarAnalyzer(original_grammar)
    analyzer.run_full_analysis()

    # 2. Initialize the parser with the generated table
    parser = PredictiveParser(
        parsing_table=analyzer.parsing_table,
        non_terminals=analyzer.final_grammar.keys(),
        start_symbol=analyzer.start_symbol
    )

    # 3. Launch the UI, passing both the parser and the analyzer for display
    app = ParserApp(parser, analyzer)
    app.mainloop()

if __name__ == "__main__":
    main()