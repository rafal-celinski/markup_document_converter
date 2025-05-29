# 📝 Markup Document Converter

**Markup Document Converter** is a Python CLI tool and library for converting documents written in markup formats (like Markdown) into various output formats such as LaTeX and Typst. It is built on an Abstract Syntax Tree (AST) and is designed to be easily extensible.

---

## 📦 Installation

**Python version required:** `>=3.9`

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
poetry env activate
```

### OR

You can download the `.whl` (wheel) file directly from the our [GitHub Releases page](https://github.com/rafal-celinski/markup_document_converter/releases). Simply navigate to the latest release, find the `.whl` file under "Assets", and download it to your local machine. Once downloaded, you can install it using pip:

```bash
pip install ./markup_document_converter-{version}-py3-none-any.whl
```
---

## 🚀 CLI Usage

```console
$ markup_document_converter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit.
* `--help`: Show this message and exit.

**Commands**:

* `list-formats`: Show all supported input parsers and output converters, listing each primary name with its aliases.
* `webapp`: Run the Flask web-app.
* `convert`: Read from a file or stdin, parse to the universal AST, then render as the chosen TARGET format.

## Show all supported input parsers and output converters, listing each primary name with its aliases.

```console
$ markup_document_converter list-formats [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.


## Run the Flask web-app.

```console
$ markup_document_converter webapp [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: Host to bind to  [default: 127.0.0.1]
* `-p, --port INTEGER`: Port to listen on  [default: 5000]
* `-d, --debug`: Enable debug mode
* `--help`: Show this message and exit.


## Read from a file or stdin, parse to the universal AST, then render as the chosen TARGET format.


```console
$ markup_document_converter convert [OPTIONS] [INPUT]
```

**Arguments**:

* `[INPUT]`: Path to the input file to convert (e.g. README.md). Omit to read from stdin.

**Options**:

* `-f, --from-format TEXT`: When reading from stdin, the input format (e.g. &#x27;markdown&#x27;).
* `-t, --to TEXT`: Target format. Choose from: latex, typst  [required]
* `-o, --output FILE`: Where to write the result. If omitted, writes to stdout.
* `--help`: Show this message and exit.


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


To Run documentation locally:

```bash
poetry run mkdocs serve -f docs/mkdocs.yml
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
