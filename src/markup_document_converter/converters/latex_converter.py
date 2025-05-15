import markup_document_converter.ast as ast
from markup_document_converter.converters.base_converter import BaseConverter
from markup_document_converter.registry import register_converter


@register_converter("latex")
class LatexConverter(BaseConverter):
    """
    AST -> LaTeX converter.

    Wraps the document in a minimal article class,
    maps AST nodes to LaTeX commands/environments.
    """

    def convert_default(self, node: ast.ASTNode) -> str:
        return "".join(child.convert(self) for child in node.children)

    def convert_document(self, document: ast.Document) -> str:
        body = "".join(child.convert(self) for child in document.children)
        return (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage[T1]{fontenc}\n"
            "\\usepackage{hyperref}\n"
            "\\usepackage{graphicx}\n"
            "\\usepackage[normalem]{ulem}\n"
            "\\usepackage{booktabs}\n"
            "\\begin{document}\n"
            f"{body}\n"
            "\\end{document}\n"
        )

    def convert_heading(self, heading: ast.Heading) -> str:
        level_map = {1: "section", 2: "subsection", 3: "subsubsection"}
        cmd = level_map.get(heading.level, "paragraph")
        title = "".join(child.convert(self) for child in heading.children)
        return f"\\{cmd}{{{title}}}\n\n"

    def convert_paragraph(self, paragraph: ast.Paragraph) -> str:
        text = "".join(child.convert(self) for child in paragraph.children)
        return f"{text}\n\n"

    def convert_text(self, text: ast.Text) -> str:
        escapes = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        return "".join(escapes.get(ch, ch) for ch in text.text)

    def convert_bold(self, bold: ast.Bold) -> str:
        content = "".join(child.convert(self) for child in bold.children)
        return f"\\textbf{{{content}}}"

    def convert_italic(self, italic: ast.Italic) -> str:
        content = "".join(child.convert(self) for child in italic.children)
        return f"\\textit{{{content}}}"

    def convert_strike(self, strike: ast.Strike) -> str:
        content = "".join(child.convert(self) for child in strike.children)
        return f"\\sout{{{content}}}"

    def convert_line_break(self, line_break: ast.LineBreak) -> str:
        return "\n\n"

    def convert_blockquote(self, blockquote: ast.Blockquote) -> str:
        inner = "".join(child.convert(self) for child in blockquote.children)
        return f"\\begin{{quote}}\n{inner}\\end{{quote}}\n\n"

    def convert_list(self, list_node: ast.List) -> str:
        env = "itemize" if list_node.list_type == "unordered" else "enumerate"
        items = "".join(child.convert(self) for child in list_node.children)
        return f"\\begin{{{env}}}\n{items}\\end{{{env}}}\n\n"

    def convert_list_item(self, list_item: ast.ListItem) -> str:
        content = "".join(child.convert(self) for child in list_item.children)
        return f"  \\item {content}\n"

    def convert_task_list_item(self, task_list_item: ast.TaskListItem) -> str:
        box = r"$\boxtimes$" if task_list_item.checked else r"$\square$"
        content = "".join(child.convert(self) for child in task_list_item.children)
        return f"  \\item[{box}] {content}\n"

    def convert_code_block(self, code_block: ast.CodeBlock) -> str:
        lang = code_block.language or "text"
        return (
            f"\\begin{{lstlisting}}[language={lang}]\n"
            f"{code_block.code}"
            "\\end{lstlisting}\n\n"
        )

    def convert_inline_code(self, inline_code: ast.InlineCode) -> str:
        text = inline_code.code
        return f"\\texttt{{{text}}}"

    def convert_image(self, image: ast.Image) -> str:
        alt = image.alt_text or ""
        return (
            f"\\begin{{figure}}[h]\n"
            f"  \\centering\n"
            f"  \\includegraphics[width=\\linewidth]{{{image.source}}}\n"
            f"  \\caption{{{alt}}}\n"
            f"\\end{{figure}}\n\n"
        )

    def convert_link(self, link: ast.Link) -> str:
        href = link.source
        text = "".join(child.convert(self) for child in link.children) or href
        return f"\\href{{{href}}}{{{text}}}"

    def convert_horizontal_rule(self, hr: ast.HorizontalRule) -> str:
        return "\\noindent\\rule{\\linewidth}{0.4pt}\n\n"

    def convert_table_row(self, table_row: ast.TableRow) -> str:
        cells = [child.convert(self) for child in table_row.children]
        if table_row.is_header:
            cells = [f"\\textbf{{{cell}}}" for cell in cells]
        return " & ".join(cells) + " \\\\"

    def convert_table(self, table: ast.Table) -> str:
        if not table.children:
            return ""
        cols = max(len(r.children) for r in table.children)
        fmt = "|".join(["l"] * cols)
        rows = []

        rows.append("\\toprule")

        for row in table.children:
            rows.append(row.convert(self))
            if row.is_header:
                rows.append("\\midrule")

        rows.append("\\bottomrule")

        body = "\n".join(rows)
        return f"\\begin{{tabular}}{{|{fmt}|}}\n{body}\n\\end{{tabular}}\n\n"

    def convert_table_cell(self, table_cell: ast.TableCell) -> str:
        return "".join(child.convert(self) for child in table_cell.children)
