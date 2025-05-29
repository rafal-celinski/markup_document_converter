from abc import ABC, abstractmethod
import markup_document_converter.ast_tree as ast_tree


class BaseConverter(ABC):
    """
    Abstract base class for document converters implementing the Visitor pattern.

    This class defines the interface for converting AST nodes to different output formats.
    Each concrete converter implementation should inherit from this class and implement
    all abstract methods to handle specific node types.

    The Visitor pattern allows adding new operations (converters) to the AST nodes
    without modifying the node classes themselves.
    """

    @abstractmethod
    def convert_default(self, node: ast_tree.ASTNode) -> str:
        """
        Convert a generic AST node to string representation.

        This method serves as a fallback for node types that don't have
        specific conversion methods implemented.

        Args:
            node (ast_tree.ASTNode): The AST node to convert.

        Returns:
            str: The string representation of the node.
        """
        pass

    @abstractmethod
    def convert_document(self, document: ast_tree.Document) -> str:
        """
        Convert a document node to string representation.

        Args:
            document (ast_tree.Document): The document node to convert.

        Returns:
            str: The string representation of the document.
        """
        pass

    @abstractmethod
    def convert_heading(self, heading: ast_tree.Heading) -> str:
        """
        Convert a heading node to string representation.

        Args:
            heading (ast_tree.Heading): The heading node to convert.

        Returns:
            str: The string representation of the heading.
        """
        pass

    @abstractmethod
    def convert_bold(self, bold: ast_tree.Bold) -> str:
        """
        Convert a bold text node to string representation.

        Args:
            bold (ast_tree.Bold): The bold text node to convert.

        Returns:
            str: The string representation of the bold text.
        """
        pass

    @abstractmethod
    def convert_italic(self, italic: ast_tree.Italic) -> str:
        """
        Convert an italic text node to string representation.

        Args:
            italic (ast_tree.Italic): The italic text node to convert.

        Returns:
            str: The string representation of the italic text.
        """
        pass

    @abstractmethod
    def convert_strike(self, strike: ast_tree.Strike) -> str:
        """
        Convert a strikethrough text node to string representation.

        Args:
            strike (ast_tree.Strike): The strikethrough text node to convert.

        Returns:
            str: The string representation of the strikethrough text.
        """
        pass

    @abstractmethod
    def convert_text(self, text: ast_tree.Text) -> str:
        """
        Convert a text node to string representation.

        Args:
            text (ast_tree.Text): The text node to convert.

        Returns:
            str: The string representation of the text.
        """
        pass

    @abstractmethod
    def convert_paragraph(self, paragraph: ast_tree.Paragraph) -> str:
        """
        Convert a paragraph node to string representation.

        Args:
            paragraph (ast_tree.Paragraph): The paragraph node to convert.

        Returns:
            str: The string representation of the paragraph.
        """
        pass

    @abstractmethod
    def convert_line_break(self, line_break: ast_tree.LineBreak) -> str:
        """
        Convert a line break node to string representation.

        Args:
            line_break (ast_tree.LineBreak): The line break node to convert.

        Returns:
            str: The string representation of the line break.
        """
        pass

    @abstractmethod
    def convert_blockquote(self, blockquote: ast_tree.Blockquote) -> str:
        """
        Convert a blockquote node to string representation.

        Args:
            blockquote (ast_tree.Blockquote): The blockquote node to convert.

        Returns:
            str: The string representation of the blockquote.
        """
        pass

    @abstractmethod
    def convert_list(self, list_node: ast_tree.List) -> str:
        """
        Convert a list node to string representation.

        Args:
            list_node (ast_tree.List): The list node to convert.

        Returns:
            str: The string representation of the list.
        """
        pass

    @abstractmethod
    def convert_list_item(self, list_item: ast_tree.ListItem) -> str:
        """
        Convert a list item node to string representation.

        Args:
            list_item (ast_tree.ListItem): The list item node to convert.

        Returns:
            str: The string representation of the list item.
        """
        pass

    @abstractmethod
    def convert_code_block(self, code_block: ast_tree.CodeBlock) -> str:
        """
        Convert a code block node to string representation.

        Args:
            code_block (ast_tree.CodeBlock): The code block node to convert.

        Returns:
            str: The string representation of the code block.
        """
        pass

    @abstractmethod
    def convert_inline_code(self, inline_code: ast_tree.InlineCode) -> str:
        """
        Convert an inline code node to string representation.

        Args:
            inline_code (ast_tree.InlineCode): The inline code node to convert.

        Returns:
            str: The string representation of the inline code.
        """
        pass

    @abstractmethod
    def convert_image(self, image: ast_tree.Image) -> str:
        """
        Convert an image node to string representation.

        Args:
            image (ast_tree.Image): The image node to convert.

        Returns:
            str: The string representation of the image.
        """
        pass

    @abstractmethod
    def convert_link(self, link: ast_tree.Link) -> str:
        """
        Convert a link node to string representation.

        Args:
            link (ast_tree.Link): The link node to convert.

        Returns:
            str: The string representation of the link.
        """
        pass

    @abstractmethod
    def convert_horizontal_rule(self, horizontal_rule: ast_tree.HorizontalRule) -> str:
        """
        Convert a horizontal rule node to string representation.

        Args:
            horizontal_rule (ast_tree.HorizontalRule): The horizontal rule node to convert.

        Returns:
            str: The string representation of the horizontal rule.
        """
        pass

    @abstractmethod
    def convert_table(self, table: ast_tree.Table) -> str:
        """
        Convert a table node to string representation.

        Args:
            table (ast_tree.Table): The table node to convert.

        Returns:
            str: The string representation of the table.
        """
        pass

    @abstractmethod
    def convert_table_row(self, table_row: ast_tree.TableRow) -> str:
        """
        Convert a table row node to string representation.

        Args:
            table_row (ast_tree.TableRow): The table row node to convert.

        Returns:
            str: The string representation of the table row.
        """
        pass

    @abstractmethod
    def convert_table_cell(self, table_cell: ast_tree.TableCell) -> str:
        """
        Convert a table cell node to string representation.

        Args:
            table_cell (ast_tree.TableCell): The table cell node to convert.

        Returns:
            str: The string representation of the table cell.
        """
        pass

    @abstractmethod
    def convert_task_list_item(self, task_list_item: ast_tree.TaskListItem) -> str:
        """
        Convert a task list item node to string representation.

        Args:
            task_list_item (ast_tree.TaskListItem): The task list item node to convert.

        Returns:
            str: The string representation of the task list item.
        """
        pass
