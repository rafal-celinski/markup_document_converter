import pytest
from markup_document_converter.core import convert_document, get_content


class TestGetContent:
    def test_read_file_content(self, tmp_path):
        # Create a test file with content
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello\nWorld")

        # Test reading content
        content = get_content(str(test_file))
        assert content == "Hello\nWorld\n"

    def test_read_empty_file(self, tmp_path):
        # Create an empty file
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        # Test reading empty file
        content = get_content(str(empty_file))
        assert content == "\n"

    def test_read_file_without_newline(self, tmp_path):
        # Create a file without trailing newline
        test_file = tmp_path / "test.txt"
        test_file.write_text("No newline at end")

        # Test that newline is added
        content = get_content(str(test_file))
        assert content == "No newline at end\n"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_content("nonexistent_file.txt")


class TestConvertDocument:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            convert_document("nonexistent_file.md", "latex")

    def test_invalid_format(self, tmp_path):
        # Create a test markdown file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        # Test with invalid format
        with pytest.raises(ValueError):
            convert_document(str(test_file), "invalid_format")

    def test_markdown_to_latex_basic(self, tmp_path):
        # Create a basic markdown file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nHello World")

        # Convert to LaTeX
        result = convert_document(str(test_file), "latex")

        # Check basic LaTeX structure
        assert "\\documentclass{article}" in result
        assert "\\section{Test}" in result
        assert "Hello World" in result
        assert "\\end{document}" in result

    def test_markdown_to_typst_basic(self, tmp_path):
        # Create a basic markdown file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nHello World")

        # Convert to Typst
        result = convert_document(str(test_file), "typst")

        # Check basic Typst structure
        assert "= Test" in result
        assert "Hello World" in result

    def test_markdown_with_formatting(self, tmp_path):
        # Create a markdown file with various formatting
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """# Test

*Italic* and **bold** text with `code`.

## Subsection

1. First item
2. Second item

> Blockquote
"""
        )

        # Convert to LaTeX
        result = convert_document(str(test_file), "latex")

        # Check formatting
        assert "\\section{Test}" in result
        assert "\\textit{Italic}" in result
        assert "\\textbf{bold}" in result
        assert "\\texttt{code}" in result
        assert "\\subsection{Subsection}" in result
        assert "\\begin{enumerate}" in result
        assert "\\begin{quote}" in result

    def test_markdown_with_table(self, tmp_path):
        # Create a markdown file with a table
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """# Test

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        )

        # Convert to LaTeX
        result = convert_document(str(test_file), "latex")

        # Check table conversion
        assert "\\begin{tabular}" in result
        assert "\\textbf{Header 1}" in result
        assert "\\textbf{Header 2}" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
        assert "Cell 3" in result
        assert "Cell 4" in result
        assert "\\end{tabular}" in result

    def test_markdown_with_code_block(self, tmp_path):
        # Create a markdown file with a code block
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """# Test

```python
def hello():
    print("Hello, World!")
```
"""
        )

        # Convert to LaTeX
        result = convert_document(str(test_file), "latex")

        # Check code block conversion
        assert "\\begin{lstlisting}[language=python]" in result
        assert "def hello():" in result
        assert 'print("Hello, World!")' in result
        assert "\\end{lstlisting}" in result

    def test_markdown_with_links_and_images(self, tmp_path):
        # Create a markdown file with links and images
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """# Test

[Link text](https://example.com)
![Alt text](image.png)
"""
        )

        # Convert to LaTeX
        result = convert_document(str(test_file), "latex")

        # Check link and image conversion
        assert "\\href{https://example.com}{Link text}" in result
        assert "\\includegraphics" in result
        assert "\\caption{Alt text}" in result
