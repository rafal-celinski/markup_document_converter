import markup_document_converter.ast_tree as ast
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
        """
        Default fallback converter for unknown node types.

        Args:
            node (ASTNode): The node to convert.

        Returns:
            str: LaTeX representation of the node's children.
        """
        return "".join(child.convert(self) for child in node.children)

    def convert_document(self, document: ast.Document) -> str:
        """
        Convert the root document node to LaTeX.

        Args:
            document (Document): The root document node.

        Returns:
            str: Full LaTeX document as a string.
        """
        body = "".join(child.convert(self) for child in document.children)
        return (
            "\\documentclass{article}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage[T1]{fontenc}\n"
            "\\usepackage{hyperref}\n"
            "\\usepackage{graphicx}\n"
            "\\usepackage[normalem]{ulem}\n"
            "\\usepackage{listings}\n"
            "\\usepackage{booktabs}\n"
            "\\usepackage{xcolor}\n"
            "\\begin{document}\n"
            f"{body}\n"
            "\\end{document}\n"
        )

    def convert_heading(self, heading: ast.Heading) -> str:
        """
        Convert a heading node to a LaTeX section command.

        Args:
            heading (Heading): The heading node.

        Returns:
            str: Corresponding LaTeX section/subsection/etc.
        """
        level_map = {1: "section", 2: "subsection", 3: "subsubsection"}
        cmd = level_map.get(heading.level, "paragraph")
        title = "".join(child.convert(self) for child in heading.children)
        return f"\\{cmd}{{{title}}}\n\n"

    def convert_paragraph(self, paragraph: ast.Paragraph) -> str:
        """
        Convert a paragraph node to LaTeX.

        Args:
            paragraph (Paragraph): The paragraph node.

        Returns:
            str: Paragraph text followed by a newline.
        """
        text = "".join(child.convert(self) for child in paragraph.children)
        return f"{text}\n\n"

    def convert_text(self, text: ast.Text) -> str:
        """
        Convert plain text with LaTeX character escaping.

        Args:
            text (Text): The text node.

        Returns:
            str: Escaped LaTeX string.
        """
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
        """
        Convert bold formatting to LaTeX.

        Args:
            bold (Bold): Bold node.

        Returns:
            str: \textbf wrapped content.
        """
        content = "".join(child.convert(self) for child in bold.children)
        return f"\\textbf{{{content}}}"

    def convert_italic(self, italic: ast.Italic) -> str:
        """
        Convert italic formatting to LaTeX.

        Args:
            italic (Italic): Italic node.

        Returns:
            str: \textit wrapped content.
        """
        content = "".join(child.convert(self) for child in italic.children)
        return f"\\textit{{{content}}}"

    def convert_strike(self, strike: ast.Strike) -> str:
        """
        Convert strikethrough formatting to LaTeX.

        Args:
            strike (Strike): Strike node.

        Returns:
            str: \\sout wrapped content.
        """
        content = "".join(child.convert(self) for child in strike.children)
        return f"\\sout{{{content}}}"

    def convert_line_break(self, line_break: ast.LineBreak) -> str:
        """
        Convert a line break to LaTeX (double newline).

        Args:
            line_break (LineBreak): Line break node.

        Returns:
            str: Two newline characters.
        """
        return "\n\n"

    def convert_blockquote(self, blockquote: ast.Blockquote) -> str:
        """
        Convert blockquote to LaTeX quote environment.

        Args:
            blockquote (Blockquote): Blockquote node.

        Returns:
            str: Content wrapped in quote environment.
        """
        inner = "".join(child.convert(self) for child in blockquote.children)
        return f"\\begin{{quote}}\n{inner}\\end{{quote}}\n\n"

    def convert_list(self, list_node: ast.List) -> str:
        """
        Convert a list node to itemize or enumerate.

        Args:
            list_node (List): List node.

        Returns:
            str: LaTeX list environment.
        """
        env = "itemize" if list_node.list_type == "unordered" else "enumerate"
        items = "".join(child.convert(self) for child in list_node.children)
        return f"\\begin{{{env}}}\n{items}\\end{{{env}}}\n\n"

    def convert_list_item(self, list_item: ast.ListItem) -> str:
        """
        Convert a list item to LaTeX \\item.

        Args:
            list_item (ListItem): List item node.

        Returns:
            str: \\item line.
        """
        content = "".join(child.convert(self) for child in list_item.children)
        return f"  \\item {content}\n"

    def convert_task_list_item(self, task_list_item: ast.TaskListItem) -> str:
        """
        Convert a task list item to LaTeX with checkbox.

        Args:
            task_list_item (TaskListItem): Task list item node.

        Returns:
            str: \\item with checkbox symbol.
        """
        box = r"$\boxtimes$" if task_list_item.checked else r"$\square$"
        content = "".join(child.convert(self) for child in task_list_item.children)
        return f"  \\item[{box}] {content}\n"

    def convert_code_block(self, code_block: ast.CodeBlock) -> str:
        """
        Convert code block to LaTeX lstlisting.

        Args:
            code_block (CodeBlock): Code block node.

        Returns:
            str: lstlisting environment with code.
        """
        lang = code_block.language or "text"
        return (
            f"\\begin{{lstlisting}}[language={lang}]\n"
            f"{code_block.code}"
            "\\end{lstlisting}\n\n"
        )

    def convert_inline_code(self, inline_code: ast.InlineCode) -> str:
        """
        Convert inline code to LaTeX \texttt.

        Args:
            inline_code (InlineCode): Inline code node.

        Returns:
            str: Inline \texttt formatted string.
        """
        raw = inline_code.code or ""
        escaped = "".join(self.convert_text(ast.Text(ch)) for ch in raw)
        return f"\\texttt{{{escaped}}}"

    def convert_image(self, image: ast.Image) -> str:
        """
        Convert image node to LaTeX figure.

        Args:
            image (Image): Image node.

        Returns:
            str: LaTeX figure environment with caption.
        """
        raw_alt = image.alt_text or ""
        alt = "".join(self.convert_text(ast.Text(ch)) for ch in raw_alt)

        return (
            f"\\begin{{figure}}[h]\n"
            f"  \\centering\n"
            f"  \\includegraphics[width=\\linewidth]{{{image.source}}}\n"
            f"  \\caption{{{alt}}}\n"
            f"\\end{{figure}}\n\n"
        )

    def convert_link(self, link: ast.Link) -> str:
        """
        Convert a hyperlink node to LaTeX \\href.

        Args:
            link (Link): Link node.

        Returns:
            str: \\href command with link and text.
        """
        href = link.source
        text = "".join(child.convert(self) for child in link.children) or href
        return f"\\href{{{href}}}{{{text}}}"

    def convert_horizontal_rule(self, hr: ast.HorizontalRule) -> str:
        """
        Convert horizontal rule to LaTeX rule command.

        Args:
            hr (HorizontalRule): Horizontal rule node.

        Returns:
            str: Rule across the page width.
        """
        return "\\noindent\\rule{\\linewidth}{0.4pt}\n\n"

    def convert_table_row(self, table_row: ast.TableRow) -> str:
        """
        Convert a table row node to LaTeX row syntax.

        Args:
            table_row (TableRow): Table row node.

        Returns:
            str: Formatted LaTeX row.
        """
        cells = [child.convert(self) for child in table_row.children]
        if table_row.is_header:
            cells = [f"\\textbf{{{cell}}}" for cell in cells]
        return " & ".join(cells) + " \\\\"

    def convert_table(self, table: ast.Table) -> str:
        """
        Convert a table node to LaTeX tabular environment.

        Args:
            table (Table): Table node.

        Returns:
            str: LaTeX tabular representation.
        """
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
        """
        Convert a table cell node to LaTeX.

        Args:
            table_cell (TableCell): Table cell node.

        Returns:
            str: LaTeX content of the cell.
        """
        return "".join(child.convert(self) for child in table_cell.children)
