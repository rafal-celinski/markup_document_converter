import pytest
from markup_document_converter.core import convert_document


class TestConvertDocument:
    def test_invalid_format(self):
        content = "# Test\n"
        with pytest.raises(ValueError):
            convert_document(content, "md", "invalid_format")

    def test_markdown_to_latex_basic(self):
        content = "# Test\n\nHello World\n"
        result = convert_document(content, "md", "latex")
        assert "\\documentclass{article}" in result
        assert "\\section{Test}" in result
        assert "Hello World" in result
        assert "\\end{document}" in result

    def test_markdown_to_typst_basic(self):
        content = "# Test\n\nHello World\n"
        result = convert_document(content, "md", "typst")
        assert "= Test" in result
        assert "Hello World" in result

    def test_markdown_with_formatting(self):
        content = (
            "# Test\n\n"
            "*Italic* and **bold** text with `code`.\n\n"
            "## Subsection\n\n"
            "1. First item\n"
            "2. Second item\n\n"
            "> Blockquote\n"
        )
        result = convert_document(content, "md", "latex")
        assert "\\section{Test}" in result
        assert "\\textit{Italic}" in result
        assert "\\textbf{bold}" in result
        assert "\\texttt{code}" in result
        assert "\\subsection{Subsection}" in result
        assert "\\begin{enumerate}" in result
        assert "\\begin{quote}" in result

    def test_markdown_with_table(self):
        content = (
            "# Test\n\n"
            "| Header 1 | Header 2 |\n"
            "|----------|----------|\n"
            "| Cell 1   | Cell 2   |\n"
            "| Cell 3   | Cell 4   |\n"
        )
        result = convert_document(content, "md", "latex")
        assert "\\begin{tabular}" in result
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
        assert "Cell 3" in result
        assert "Cell 4" in result
        assert "\\end{tabular}" in result

    def test_markdown_with_code_block(self):
        content = (
            "# Test\n\n"
            "```python\n"
            "def hello():\n"
            '    print("Hello, World!")\n'
            "```\n"
        )
        result = convert_document(content, "md", "latex")
        assert "\\begin{lstlisting}[language=python]" in result
        assert "def hello()" in result
        assert 'print("Hello, World!")' in result
        assert "\\end{lstlisting}" in result

    def test_markdown_with_links_and_images(self):
        content = (
            "# Test\n\n" "[Link text](https://example.com)\n" "![Alt text](image.png)\n"
        )
        result = convert_document(content, "md", "latex")
        assert "\\href{https://example.com}{Link text}" in result
        assert "\\includegraphics" in result
        assert "\\caption{Alt text}" in result
