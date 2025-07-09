# Predictive Parser Desktop Application

A modular, professional desktop application for predictive parsing using Tkinter.

## Features
- Non-recursive predictive parser for a sample grammar
- Professional Tkinter GUI with parsing steps table
- Modular codebase for easy maintenance and extension

## Folder Structure
```
compiler/
├── parser/
│   ├── __init__.py
│   └── predictive_parser.py
├── ui/
│   ├── __init__.py
│   └── app.py
├── main.py
├── requirements.txt
└── README.md
```

## How to Run
1. Ensure you have Python 3 installed (Tkinter is included by default).
2. From the `compiler` directory, run:
   ```sh
   python main.py
   ```

## Project Modules
- `parser/predictive_parser.py`: Contains the `PredictiveParser` class and parsing logic.
- `ui/app.py`: Contains the `ParserApp` Tkinter GUI class.
- `main.py`: Entry point to launch the application.

## License
MIT 