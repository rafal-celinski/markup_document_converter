# 📝 Markup Document Converter

**Markup Document Converter** is a Python CLI tool and library for converting documents written in markup formats (like Markdown) into various output formats such as LaTeX and Typst. It is built on an Abstract Syntax Tree (AST) and is designed to be easily extensible.

---

## 📦 Installation

**Python version required:** `>=3.13`

1. Clone the repository:

```bash
git clone https://github.com/rafal-celinski/markup_document_converter
cd markup-document-converter
```

2. Install dependencies with [Poetry](https://python-poetry.org/):

```bash
poetry install
```

3. Activate the virtual environment:

```bash
poetry shell
```

---

## 🛠 Project Structure

```
markup_document_converter/
├── converters/       # Output converters (e.g., Typst, LaTeX)
├── parsers/          # Input parsers (e.g., Markdown)
├── ast_tree.py       # AST node classes
├── registry.py       # Parser and converter registration
├── cli.py            # CLI built with Typer
└── core.py           # Core conversion logic
```

---

## 📚 Generating Documentation

This project uses **MkDocs** with `mkdocstrings` and `mkdocs-material`.

1. Install documentation dependencies:

```bash
poetry add --group docs mkdocs mkdocstrings[python] mkdocs-material
```

2. Run documentation locally:

```bash
poetry run mkdocs serve
```

Docs will be available at: [http://localhost:8000](http://localhost:8000)

---

## ✅ Running Tests

Tests are written with `pytest`. Run them using:

```bash
poetry run pytest
```

---

## 💡 Extending the Project

To add a new format (parser or converter):

1. Create a class that inherits from `BaseParser` or `BaseConverter`.
2. Register it using `@register_parser` or `@register_converter`.
3. Implement the required methods.
4. Add tests and update documentation.

---

## 👤 Authors

Developed by

* **Mateusz Łukasiewicz**
* **Przemysław Walecki**
* **Rafał Celiński**

---
