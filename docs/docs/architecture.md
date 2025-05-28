# Project Architecture

The project uses a modular architecture with:

- **Parsers**: Convert input documents to AST.
- **Converters**: Convert AST to output formats.
- **Registry**: Dynamically connects parsers and converters.
- **AST Tree**: Unified structure representing documents.

Key Modules:
- `ast_tree.py`: Defines all AST nodes
- `converters/`: Output formatters (LaTeX, Typst)
- `parsers/`: Input readers that produce AST (currently only Markdown)
