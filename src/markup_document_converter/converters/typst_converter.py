from markup_document_converter.converters.base_converter import BaseConverter
import markup_document_converter.ast as ast


class TypstConverter(BaseConverter):
    def _add_markup(self, left, right, node):
        chidren_result = "".join([child.convert(self) for child in node.children])
        return f"{left}{chidren_result}{right}"

    def convert_default(self, node: ast.ASTNode) -> str:
        pass

    def convert_document(self, document: ast.Document) -> str:
        return self._add_markup("", "\n", document)

    def convert_heading(self, heading: ast.Heading) -> str:
        return self._add_markup(f"\n{'=' * heading.level} ", "\n", heading)

    def convert_bold(self, bold: ast.Bold) -> str:
        return self._add_markup("*", "*", bold)

    def convert_italic(self, italic: ast.Italic) -> str:
        return self._add_markup("_", "_", italic)

    def convert_strike(self, strike: ast.Strike) -> str:
        return self._add_markup("#strike[", "]", strike)

    def convert_text(self, text: ast.Text) -> str:
        return text.text

    def convert_paragraph(self, paragraph: ast.Paragraph) -> str:
        return self._add_markup("\n", "\n", paragraph)

    def convert_line_break(self, line_break: ast.LineBreak) -> str:
        return "\\ "

    def convert_blockquote(self, blockquote: ast.Blockquote) -> str:
        return self._add_markup("#quote[", "]", blockquote)

    def convert_list(self, list_node: ast.List) -> str:

        result = "\n"

        for child in list_node.children:
            if list_node.list_type == "unordered":
                marker = "-"  # unordered
            elif child.order is None:
                marker = "+"  # auto ordered
            else:
                marker = f"{child.order}."  # ordered

            result += f"{marker} " + child.convert(self) + "\n"

        return result

    def convert_list_item(self, list_item: ast.ListItem) -> str:
        chidren_result = "".join([child.convert(self) for child in list_item.children])
        return chidren_result

    def convert_code_block(self, code_block: ast.CodeBlock) -> str:
        return f"```{code_block.language}\n" + f"{code_block.code}\n```"

    def convert_inline_code(self, inline_code: ast.InlineCode) -> str:
        return f"```{inline_code.language} {inline_code.code}```"

    def convert_image(self, image: ast.Image) -> str:
        return f'#image("{image.source}", alt: "{image.alt_text}")'

    def convert_link(self, link: ast.Link) -> str:
        link_text = "".join([child.convert(self) for child in link.children])

        return f'#link("{link.source}")' + (f"[{link_text}]" if link.children else "")

    def convert_horizontal_rule(self, horizontal_rule: ast.HorizontalRule) -> str:
        return "#line(length: 100%)"

    def convert_table(self, table: ast.Table) -> str:

        columns = 0
        for row in table.children:
            columns = max(columns, len(row.children))

        result = f"\n#table(\n\tcolumns: {columns},\n"

        for row in table.children:
            result += "\t"
            for cell in row.children:
                result += f"[{cell.convert(self)}], "
            result += "[], " * (columns - len(row.children))
            result += "\n"

        result += ")\n"

        return result

    def convert_table_row(self, table_row: ast.TableRow) -> str:
        pass

    def convert_table_cell(self, table_cell: ast.TableCell) -> str:
        cell_text = "".join([child.convert(self) for child in table_cell.children])
        return cell_text

    def convert_task_list_item(self, task_list_item: ast.TaskListItem) -> str:
        if task_list_item.checked:
            return self._add_markup("\n[x] ", "\n", task_list_item)
        else:
            return self._add_markup("\n[ ] ", "\n", task_list_item)
