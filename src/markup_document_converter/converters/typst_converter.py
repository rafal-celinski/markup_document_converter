from markup_document_converter.converters.base_converter import BaseConverter
from markup_document_converter.registry import register_converter
import markup_document_converter.ast_tree as ast_tree


@register_converter("typst")
class TypstConverter(BaseConverter):
    def _add_markup(self, left, right, node):
        chidren_result = "".join([child.convert(self) for child in node.children])
        return f"{left}{chidren_result}{right}"

    def convert_default(self, node: ast_tree.ASTNode) -> str:
        return ""

    def convert_document(self, document: ast_tree.Document) -> str:
        return self._add_markup("", "\n", document)

    def convert_heading(self, heading: ast_tree.Heading) -> str:
        return self._add_markup(f"\n{'=' * heading.level} ", "\n", heading)

    def convert_bold(self, bold: ast_tree.Bold) -> str:
        return self._add_markup("*", "*", bold)

    def convert_italic(self, italic: ast_tree.Italic) -> str:
        return self._add_markup("_", "_", italic)

    def convert_strike(self, strike: ast_tree.Strike) -> str:
        return self._add_markup("#strike[", "]", strike)

    def convert_text(self, text: ast_tree.Text) -> str:
        result = text.text

        typst_special_chars = [
            "\\",
            "*",
            "#",
            "[",
            "]",
            "+",
            "-",
            "/",
            "$",
            "=",
            "<",
            ">",
            "@",
            "'",
            '"',
            "`",
        ]

        unusual_escapes = {
            "_ ": "\\_ ",
            " _": " \\_",
        }

        # escape special chars
        for char in typst_special_chars:
            result = result.replace(char, f"\\{char}")

        for char, escape_char in unusual_escapes.items():
            result = result.replace(char, escape_char)

        return result

    def convert_paragraph(self, paragraph: ast_tree.Paragraph) -> str:
        return self._add_markup("\n", "\n", paragraph)

    def convert_line_break(self, line_break: ast_tree.LineBreak) -> str:
        return "\\ "

    def convert_blockquote(self, blockquote: ast_tree.Blockquote) -> str:
        return self._add_markup("#quote[", "]", blockquote)

    def convert_list(self, list_node: ast_tree.List) -> str:
        def add_indent(text: str, indent: str):
            has_trailing_newline = text.endswith("\n")
            if has_trailing_newline:
                text = text[:-1]

            text = text.replace("\n", f"\n{indent}")

            if has_trailing_newline:
                text = text + "\n"
            return text

        indent = "\t"
        result = "\n"

        for child in list_node.children:
            if list_node.list_type == "unordered":
                marker = "-"
            elif child.order is not None:
                marker = f"{child.order}."
            else:
                marker = "+"

            child_content = child.convert(self)

            child_content = add_indent(child_content, indent)

            result += f"{marker} {child_content}"

        return result

    def convert_list_item(self, list_item: ast_tree.ListItem) -> str:
        children_result = "".join([child.convert(self) for child in list_item.children])

        if not children_result.endswith("\n"):
            children_result += "\n"

        return children_result

    def convert_task_list_item(self, task_list_item: ast_tree.TaskListItem) -> str:
        if task_list_item.checked:
            return self._add_markup("[x] ", "\n", task_list_item)
        else:
            return self._add_markup("[ ] ", "\n", task_list_item)

    def convert_code_block(self, code_block: ast_tree.CodeBlock) -> str:
        return (
            f"```{code_block.language if code_block.language else ''}\n"
            + f"{code_block.code}\n```"
        )

    def convert_inline_code(self, inline_code: ast_tree.InlineCode) -> str:
        return f"```{inline_code.language+' ' if inline_code.language else ''}{inline_code.code}```"

    def convert_image(self, image: ast_tree.Image) -> str:
        result = f'#image("{image.source}"'

        if image.alt_text:
            result += f', alt: "{image.alt_text}"'
        result += ")"

        return result

    def convert_link(self, link: ast_tree.Link) -> str:
        link_text = "".join([child.convert(self) for child in link.children])

        return f'#link("{link.source}")' + (f"[{link_text}]" if link.children else "")

    def convert_horizontal_rule(self, horizontal_rule: ast_tree.HorizontalRule) -> str:
        return "#line(length: 100%)"

    def convert_table(self, table: ast_tree.Table) -> str:

        columns = 0
        for row in table.children:
            columns = max(columns, len(row.children))

        result = f"\n#table(\n\tcolumns: {columns},\n"

        for row in table.children:
            result += "\t"
            result += row.convert(self)

            if not row.is_header:
                result += "[], " * (columns - len(row.children))

            result += "\n"

        result += ")\n"

        return result

    def convert_table_row(self, table_row: ast_tree.TableRow) -> str:
        result = ""
        for cell in table_row.children:
            result += f"[{cell.convert(self)}], "

        if table_row.is_header:
            result = f"table.header({result}),"
        return result

    def convert_table_cell(self, table_cell: ast_tree.TableCell) -> str:
        cell_text = "".join([child.convert(self) for child in table_cell.children])
        return cell_text
