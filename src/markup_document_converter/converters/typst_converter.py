from markup_document_converter.converters.base_converter import BaseConverter
from markup_document_converter.registry import register_converter
import markup_document_converter.ast_tree as ast_tree


@register_converter("typst")
class TypstConverter(BaseConverter):
    """
    Concrete implementation of BaseConverter for Typst markup language.

    This converter transforms AST nodes into Typst markup syntax, implementing
    the Visitor pattern. Typst is a modern markup-based typesetting system
    designed for scientific documents.

    The converter handles all standard document elements including text formatting,
    lists, tables, code blocks, images, and links, converting them to their
    Typst equivalents.
    """

    def _add_markup(self, left, right, node):
        """
        Helper method to wrap node children with markup delimiters.

        Args:
            left (str): Left delimiter/markup to add before content.
            right (str): Right delimiter/markup to add after content.
            node (ast_tree.ASTNode): The AST node whose children to process.

        Returns:
            str: The content wrapped with specified delimiters.
        """
        chidren_result = "".join([child.convert(self) for child in node.children])
        return f"{left}{chidren_result}{right}"

    def convert_default(self, node: ast_tree.ASTNode) -> str:
        """
        Convert a generic AST node to Typst representation.

        Args:
            node (ast_tree.ASTNode): The AST node to convert.

        Returns:
            str: Empty string as fallback for unsupported node types.
        """
        return ""

    def convert_document(self, document: ast_tree.Document) -> str:
        """
        Convert a document node to Typst representation.

        Args:
            document (ast_tree.Document): The document node to convert.

        Returns:
            str: The Typst representation of the document.
        """
        return self._add_markup("", "\n", document)

    def convert_heading(self, heading: ast_tree.Heading) -> str:
        """
        Convert a heading node to Typst heading syntax.

        Uses equal signs (=) to denote heading levels in Typst format.

        Args:
            heading (ast_tree.Heading): The heading node to convert.

        Returns:
            str: The Typst heading markup.
        """
        return self._add_markup(f"\n{'=' * heading.level} ", "\n", heading)

    def convert_bold(self, bold: ast_tree.Bold) -> str:
        """
        Convert a bold text node to Typst bold syntax.

        Args:
            bold (ast_tree.Bold): The bold text node to convert.

        Returns:
            str: The Typst bold markup using asterisks.
        """
        return self._add_markup("*", "*", bold)

    def convert_italic(self, italic: ast_tree.Italic) -> str:
        """
        Convert an italic text node to Typst italic syntax.

        Args:
            italic (ast_tree.Italic): The italic text node to convert.

        Returns:
            str: The Typst italic markup using underscores.
        """
        return self._add_markup("_", "_", italic)

    def convert_strike(self, strike: ast_tree.Strike) -> str:
        """
        Convert a strikethrough text node to Typst strike syntax.

        Args:
            strike (ast_tree.Strike): The strikethrough text node to convert.

        Returns:
            str: The Typst strikethrough markup using #strike function.
        """
        return self._add_markup("#strike[", "]", strike)

    def convert_text(self, text: ast_tree.Text) -> str:
        """
        Convert a text node to Typst representation with proper escaping.

        Escapes special Typst characters and handles unusual escape sequences
        to ensure proper rendering in Typst documents.

        Args:
            text (ast_tree.Text): The text node to convert.

        Returns:
            str: The escaped text suitable for Typst.
        """
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
        """
        Convert a paragraph node to Typst representation.

        Args:
            paragraph (ast_tree.Paragraph): The paragraph node to convert.

        Returns:
            str: The Typst paragraph with newline separators.
        """
        return self._add_markup("\n", "\n", paragraph)

    def convert_line_break(self, line_break: ast_tree.LineBreak) -> str:
        """
        Convert a line break node to Typst line break syntax.

        Args:
            line_break (ast_tree.LineBreak): The line break node to convert.

        Returns:
            str: The Typst line break markup.
        """
        return "\\ "

    def convert_blockquote(self, blockquote: ast_tree.Blockquote) -> str:
        """
        Convert a blockquote node to Typst quote syntax.

        Args:
            blockquote (ast_tree.Blockquote): The blockquote node to convert.

        Returns:
            str: The Typst blockquote using #quote function.
        """
        return self._add_markup("#quote[", "]", blockquote)

    def convert_list(self, list_node: ast_tree.List) -> str:
        """
        Convert a list node to Typst list syntax.

        Handles both ordered and unordered lists with proper indentation
        and appropriate markers (-, +, or numbered).

        Args:
            list_node (ast_tree.List): The list node to convert.

        Returns:
            str: The Typst list markup with proper formatting.
        """

        def add_indent(text: str, indent: str):
            """Add indentation to multi-line text while preserving structure."""
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
        """
        Convert a list item node to Typst representation.

        Args:
            list_item (ast_tree.ListItem): The list item node to convert.

        Returns:
            str: The Typst list item content with proper line ending.
        """
        children_result = "".join([child.convert(self) for child in list_item.children])

        if not children_result.endswith("\n"):
            children_result += "\n"

        return children_result

    def convert_task_list_item(self, task_list_item: ast_tree.TaskListItem) -> str:
        """
        Convert a task list item node to Typst checkbox syntax.

        Args:
            task_list_item (ast_tree.TaskListItem): The task list item node to convert.

        Returns:
            str: The Typst task list item with checkbox marker.
        """
        if task_list_item.checked:
            return self._add_markup("[x] ", "\n", task_list_item)
        else:
            return self._add_markup("[ ] ", "\n", task_list_item)

    def convert_code_block(self, code_block: ast_tree.CodeBlock) -> str:
        """
        Convert a code block node to Typst code block syntax.

        Args:
            code_block (ast_tree.CodeBlock): The code block node to convert.

        Returns:
            str: The Typst code block with optional language specification.
        """
        return (
            f"```{code_block.language if code_block.language else ''}\n"
            + f"{code_block.code}\n```"
        )

    def convert_inline_code(self, inline_code: ast_tree.InlineCode) -> str:
        """
        Convert an inline code node to Typst inline code syntax.

        Args:
            inline_code (ast_tree.InlineCode): The inline code node to convert.

        Returns:
            str: The Typst inline code with optional language specification.
        """
        return f"```{inline_code.language+' ' if inline_code.language else ''}{inline_code.code}```"

    def convert_image(self, image: ast_tree.Image) -> str:
        """
        Convert an image node to Typst image syntax.

        Args:
            image (ast_tree.Image): The image node to convert.

        Returns:
            str: The Typst image markup with optional alt text.
        """
        result = f'#image("{image.source}"'

        if image.alt_text:
            result += f', alt: "{image.alt_text}"'
        result += ")"

        return result

    def convert_link(self, link: ast_tree.Link) -> str:
        """
        Convert a link node to Typst link syntax.

        Args:
            link (ast_tree.Link): The link node to convert.

        Returns:
            str: The Typst link markup with optional link text.
        """
        link_text = "".join([child.convert(self) for child in link.children])

        return f'#link("{link.source}")' + (f"[{link_text}]" if link.children else "")

    def convert_horizontal_rule(self, horizontal_rule: ast_tree.HorizontalRule) -> str:
        """
        Convert a horizontal rule node to Typst line syntax.

        Args:
            horizontal_rule (ast_tree.HorizontalRule): The horizontal rule node to convert.

        Returns:
            str: The Typst horizontal line markup.
        """
        return "#line(length: 100%)"

    def convert_table(self, table: ast_tree.Table) -> str:
        """
        Convert a table node to Typst table syntax.

        Calculates the maximum number of columns and generates a properly
        formatted Typst table with headers and data rows.

        Args:
            table (ast_tree.Table): The table node to convert.

        Returns:
            str: The Typst table markup with proper column specification.
        """
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
        """
        Convert a table row node to Typst table row syntax.

        Args:
            table_row (ast_tree.TableRow): The table row node to convert.

        Returns:
            str: The Typst table row markup, wrapped with table.header() if it's a header row.
        """
        result = ""
        for cell in table_row.children:
            result += f"[{cell.convert(self)}], "

        if table_row.is_header:
            result = f"table.header({result}),"
        return result

    def convert_table_cell(self, table_cell: ast_tree.TableCell) -> str:
        """
        Convert a table cell node to Typst representation.

        Args:
            table_cell (ast_tree.TableCell): The table cell node to convert.

        Returns:
            str: The Typst table cell content.
        """
        cell_text = "".join([child.convert(self) for child in table_cell.children])
        return cell_text
