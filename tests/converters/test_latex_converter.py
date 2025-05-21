import pytest
import markup_document_converter.ast_tree as ast
from markup_document_converter.converters.latex_converter import LatexConverter


@pytest.fixture
def latex_converter():
    return LatexConverter()


class TestLatexConverter:
    def test_convert_default(self, latex_converter):
        node = ast.ASTNode(node_type="default")
        assert latex_converter.convert_default(node) == ""

    def test_convert_document(self, latex_converter):
        document = ast.Document(
            children=[
                ast.Heading(level=1, children=[ast.Text("Heading 1")]),
                ast.Text("Text "),
                ast.Bold(children=[ast.Text("Bold text")]),
            ]
        )

        result = document.convert(latex_converter)

        assert "\\documentclass{article}" in result
        assert "\\usepackage[utf8]{inputenc}" in result
        assert "\\usepackage[T1]{fontenc}" in result
        assert "\\usepackage{hyperref}" in result
        assert "\\usepackage{graphicx}" in result
        assert "\\usepackage[normalem]{ulem}" in result
        assert "\\usepackage{booktabs}" in result
        assert "\\section{Heading 1}" in result
        assert "Text \\textbf{Bold text}" in result
        assert "\\end{document}" in result

    def test_empty_document(self, latex_converter):
        document = ast.Document([])
        result = document.convert(latex_converter)
        assert "\\begin{document}" in result
        assert "\\end{document}" in result

    @pytest.mark.parametrize(
        "level,expected",
        [
            (1, "\\section{Heading}\n\n"),
            (2, "\\subsection{Heading}\n\n"),
            (3, "\\subsubsection{Heading}\n\n"),
            (4, "\\paragraph{Heading}\n\n"),
        ],
    )
    def test_convert_heading(self, latex_converter, level, expected):
        heading = ast.Heading(level=level, children=[ast.Text("Heading")])
        result = heading.convert(latex_converter)
        assert result == expected

    def test_empty_heading(self, latex_converter):
        heading = ast.Heading(level=1)
        result = heading.convert(latex_converter)
        assert result == "\\section{}\n\n"

    def test_convert_bold(self, latex_converter):
        bold = ast.Bold(children=[ast.Text("Bold text")])
        result = bold.convert(latex_converter)
        assert result == "\\textbf{Bold text}"

    def test_bold_empty(self, latex_converter):
        bold = ast.Bold([])
        result = bold.convert(latex_converter)
        assert result == "\\textbf{}"

    def test_convert_italic(self, latex_converter):
        italic = ast.Italic(children=[ast.Text("Italic text")])
        result = italic.convert(latex_converter)
        assert result == "\\textit{Italic text}"

    def test_empty_italic(self, latex_converter):
        italic = ast.Italic()
        result = italic.convert(latex_converter)
        assert result == "\\textit{}"

    def test_convert_strike(self, latex_converter):
        strike = ast.Strike(children=[ast.Text("Strike text")])
        result = strike.convert(latex_converter)
        assert result == "\\sout{Strike text}"

    def test_empty_strike(self, latex_converter):
        strike = ast.Strike()
        result = strike.convert(latex_converter)
        assert result == "\\sout{}"

    def test_convert_text(self, latex_converter):
        text = ast.Text("Text")
        result = text.convert(latex_converter)
        assert result == "Text"

    def test_convert_text_with_special_chars(self, latex_converter):
        text = ast.Text(r"\&%$_^{}~")
        result = text.convert(latex_converter)
        expected = (
            r"\textbackslash{}\&\%\$\_" r"\textasciicircum{}\{\}" r"\textasciitilde{}"
        )
        assert result == expected

    def test_convert_paragraph(self, latex_converter):
        paragraph = ast.Paragraph(children=[ast.Text("Paragraph")])
        result = paragraph.convert(latex_converter)
        assert result == "Paragraph\n\n"

    def test_empty_paragraph(self, latex_converter):
        paragraph = ast.Paragraph()
        result = paragraph.convert(latex_converter)
        assert result == "\n\n"

    def test_convert_line_break(self, latex_converter):
        line_break = ast.LineBreak()
        result = line_break.convert(latex_converter)
        assert result == "\n\n"

    def test_convert_blockquote(self, latex_converter):
        blockquote = ast.Blockquote(children=[ast.Text("Blockquote")])
        result = blockquote.convert(latex_converter)
        assert result == "\\begin{quote}\nBlockquote\\end{quote}\n\n"

    def test_empty_blockquote(self, latex_converter):
        blockquote = ast.Blockquote()
        result = blockquote.convert(latex_converter)
        assert result == "\\begin{quote}\n\\end{quote}\n\n"

    def test_nested_blockquote(self, latex_converter):
        blockquote = ast.Blockquote(
            children=[
                ast.Text("Blockquote "),
                ast.Blockquote(children=[ast.Text("Nested Blockquote")]),
            ]
        )
        result = blockquote.convert(latex_converter)
        expected = (
            "\\begin{quote}\n"
            "Blockquote \\begin{quote}\n"
            "Nested Blockquote\\end{quote}\n\n"
            "\\end{quote}\n\n"
        )
        assert result == expected

    def test_convert_ordered_list(self, latex_converter):
        ordered_list = ast.List(
            list_type="ordered",
            children=[
                ast.ListItem(order=1, children=[ast.Text("Item 1")]),
                ast.ListItem(order=2, children=[ast.Text("Item 2")]),
                ast.ListItem(order=3, children=[ast.Text("Item 3")]),
            ],
        )
        result = ordered_list.convert(latex_converter)
        assert "\\begin{enumerate}" in result
        assert "\\item Item 1" in result
        assert "\\item Item 2" in result
        assert "\\item Item 3" in result
        assert "\\end{enumerate}" in result

    def test_convert_unordered_list(self, latex_converter):
        unordered_list = ast.List(
            list_type="unordered",
            children=[
                ast.ListItem(children=[ast.Text("Item 1")]),
                ast.ListItem(children=[ast.Text("Item 2")]),
                ast.ListItem(children=[ast.Text("Item 3")]),
            ],
        )
        result = unordered_list.convert(latex_converter)
        assert "\\begin{itemize}" in result
        assert "\\item Item 1" in result
        assert "\\item Item 2" in result
        assert "\\item Item 3" in result
        assert "\\end{itemize}" in result

    def test_convert_task_list_item(self, latex_converter):
        task_list_item = ast.TaskListItem(checked=True, children=[ast.Text("Task")])
        result = task_list_item.convert(latex_converter)
        assert result == "  \\item[$\\boxtimes$] Task\n"

        task_list_item = ast.TaskListItem(checked=False, children=[ast.Text("Task")])
        result = task_list_item.convert(latex_converter)
        assert result == "  \\item[$\\square$] Task\n"

    def test_convert_code_block(self, latex_converter):
        code_block = ast.CodeBlock(code="print('Hello')", language="python")
        result = code_block.convert(latex_converter)
        assert "\\begin{lstlisting}[language=python]" in result
        assert "print('Hello')" in result
        assert "\\end{lstlisting}" in result

    def test_convert_inline_code(self, latex_converter):
        inline_code = ast.InlineCode(code="print('Hello')")
        result = inline_code.convert(latex_converter)
        assert result == "\\texttt{print('Hello')}"

    def test_convert_image(self, latex_converter):
        image = ast.Image(source="image.png", alt_text="Alt text")
        result = image.convert(latex_converter)
        assert "\\begin{figure}[h]" in result
        assert "\\centering" in result
        assert "\\includegraphics[width=\\linewidth]{image.png}" in result
        assert "\\caption{Alt text}" in result
        assert "\\end{figure}" in result

    def test_convert_link(self, latex_converter):
        link = ast.Link(source="example.com", children=[ast.Text("Link text")])
        result = link.convert(latex_converter)
        assert result == "\\href{example.com}{Link text}"

    def test_convert_link_without_text(self, latex_converter):
        link = ast.Link(source="example.com")
        result = link.convert(latex_converter)
        assert result == "\\href{example.com}{example.com}"

    def test_convert_horizontal_rule(self, latex_converter):
        hr = ast.HorizontalRule()
        result = hr.convert(latex_converter)
        assert result == "\\noindent\\rule{\\linewidth}{0.4pt}\n\n"

    def test_convert_table_with_header(self, latex_converter):
        table = ast.Table(
            children=[
                ast.TableRow(
                    is_header=True,
                    children=[
                        ast.TableCell(children=[ast.Text("Header 1")]),
                        ast.TableCell(children=[ast.Text("Header 2")]),
                    ],
                ),
                ast.TableRow(
                    is_header=False,
                    children=[
                        ast.TableCell(children=[ast.Text("Cell 1")]),
                        ast.TableCell(children=[ast.Text("Cell 2")]),
                    ],
                ),
            ]
        )
        result = table.convert(latex_converter)
        assert "\\begin{tabular}{|l|l|}" in result
        assert "\\toprule" in result
        assert "\\textbf{Header 1} & \\textbf{Header 2} \\\\" in result
        assert "\\midrule" in result
        assert "Cell 1 & Cell 2 \\\\" in result
        assert "\\bottomrule" in result
        assert "\\end{tabular}" in result

    def test_convert_table_without_header(self, latex_converter):
        table = ast.Table(
            children=[
                ast.TableRow(
                    is_header=False,
                    children=[
                        ast.TableCell(children=[ast.Text("Cell 1")]),
                        ast.TableCell(children=[ast.Text("Cell 2")]),
                    ],
                ),
            ]
        )
        result = table.convert(latex_converter)
        assert "\\begin{tabular}{|l|l|}" in result
        assert "\\toprule" in result
        assert "Cell 1 & Cell 2 \\\\" in result
        assert "\\bottomrule" in result
        assert "\\end{tabular}" in result

    def test_convert_empty_table(self, latex_converter):
        table = ast.Table(children=[])
        result = table.convert(latex_converter)
        assert "" in result

    def test_convert_table_row(self, latex_converter):
        row = ast.TableRow(
            is_header=False,
            children=[
                ast.TableCell(children=[ast.Text("Cell 1")]),
                ast.TableCell(children=[ast.Text("Cell 2")]),
            ],
        )
        result = row.convert(latex_converter)
        assert result == "Cell 1 & Cell 2 \\\\"

    def test_convert_table_row_header(self, latex_converter):
        row = ast.TableRow(
            is_header=True,
            children=[
                ast.TableCell(children=[ast.Text("Header 1")]),
                ast.TableCell(children=[ast.Text("Header 2")]),
            ],
        )
        result = row.convert(latex_converter)
        assert result == "\\textbf{Header 1} & \\textbf{Header 2} \\\\"

    def test_convert_table_cell(self, latex_converter):
        cell = ast.TableCell(children=[ast.Text("Cell text")])
        result = cell.convert(latex_converter)
        assert result == "Cell text"
