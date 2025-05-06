class ASTNode:
    """
    Base class for all nodes in the Abstract Syntax Tree (AST).

    Args:
        node_type (str): The type of the node.
        children (list, optional): The child nodes of this node. Defaults to None.
        attributes (dict, optional): Additional attributes for the node. Defaults to None.
    """

    def __init__(self, node_type: str, children: list = None, attributes: dict = None):
        """
        Initialize an ASTNode.

        Args:
            node_type (str): The type of the node.
            children (list, optional): List of child nodes. Defaults to None.
            attributes (dict, optional): Node attributes. Defaults to None.
        """
        self._node_type = node_type
        self._children = children or []
        self._attributes = attributes or {}

    def set_attribute(self, key: str, value):
        """
        Set an attribute for the node.

        Args:
            key (str): The attribute name.
            value: The attribute value.
        """
        self._attributes[key] = value

    @property
    def attributes(self):
        """
        dict: The attributes of the node.
        """
        return self._attributes

    def add_child(self, child):
        """
        Add a child node.

        Args:
            child (ASTNode): The child node to add.
        """
        self._children.append(child)

    @property
    def children(self):
        """
        list: The child nodes of this node.
        """
        return self._children

    def __repr__(self):
        """
        Return a string representation of the node.

        Returns:
            str: The string representation.
        """
        return (
            f"{self.__class__.__name__}(node_type={self._node_type}, "
            + f"attributes={self._attributes})"
        )

    @property
    def node_type(self):
        """
        str: The type of the node.
        """
        return self._node_type


class Document(ASTNode):
    """
    Represents the root document node in the AST.
    """

    def __init__(self, children=None):
        """
        Initialize a Document node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("document", children)


class Heading(ASTNode):
    """
    Represents a heading node with a specific level.
    """

    def __init__(self, level, children=None):
        """
        Initialize a Heading node.

        Args:
            level (int): Heading level (e.g., 1 for H1).
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("heading", children, attributes={"level": level})

    @property
    def level(self):
        """
        int: The heading level.
        """
        return self.attributes.get("level", 1)

    @level.setter
    def level(self, value):
        """
        Set the heading level.

        Args:
            value (int): The new heading level.
        """
        self.set_attribute("level", value)


class Bold(ASTNode):
    """
    Represents bold text formatting.
    """

    def __init__(self, children=None):
        """
        Initialize a Bold node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("bold", children)


class Italic(ASTNode):
    """
    Represents italic text formatting.
    """

    def __init__(self, children=None):
        """
        Initialize an Italic node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("italic", children)


class Strike(ASTNode):
    """
    Represents strikethrough text formatting.
    """

    def __init__(self, children=None):
        """
        Initialize a Strike node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("strike", children)


class Text(ASTNode):
    """
    Represents a text node containing a string.
    """

    def __init__(self, text, children=None):
        """
        Initialize a Text node.

        Args:
            text (str): The text content.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("text", children, attributes={"text": text})

    @property
    def text(self):
        """
        str: The text content.
        """
        return self.attributes.get("text", "")

    @text.setter
    def text(self, value):
        """
        Set the text content.

        Args:
            value (str): The new text content.
        """
        self.set_attribute("text", value)


class Paragraph(ASTNode):
    """
    Represents a paragraph node.
    """

    def __init__(self, children=None):
        """
        Initialize a Paragraph node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("paragraph", children)


class LineBreak(ASTNode):
    """
    Represents a line break in the document.
    """

    def __init__(self, children=None):
        """
        Initialize a LineBreak node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("line_break", children)


class Blockquote(ASTNode):
    """
    Represents a blockquote node.
    """

    def __init__(self, children=None):
        """
        Initialize a Blockquote node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("blockquote", children)


class List(ASTNode):
    """
    Represents a list node, either ordered or unordered.
    """

    def __init__(self, list_type, children=None):
        """
        Initialize a List node.

        Args:
            list_type (str): The type of the list ("ordered" or "unordered").
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("list", children, attributes={"list_type": list_type})

    @property
    def list_type(self):
        """
        str: The type of the list.
        """
        return self.attributes.get("list_type", "")

    @list_type.setter
    def list_type(self, value):
        """
        Set the list type.

        Args:
            value (str): The new list type.
        """
        self.set_attribute("list_type", value)


class ListItem(ASTNode):
    """
    Represents an item within a list.
    """

    def __init__(self, order, nesting, children=None):
        """
        Initialize a ListItem node.

        Args:
            order (int): The order of the item in the list.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__(
            "list_item", children, attributes={"order": order, "nesting": nesting}
        )

    @property
    def order(self):
        """
        int: The order of the list item.
        """
        return self.attributes.get("order", "")

    @property
    def nesting(self):
        """
        int: Nesting level of the list item
        """
        return self.attributes.get("nesting", 0)

    @order.setter
    def order(self, value):
        """
        Set the order of the list item.

        Args:
            value (int): The new order.
        """
        self.set_attribute("order", value)

    @nesting.setter
    def nesting(self, value):
        """
        Set the nesting level of the list item

        Args:
            value (int): The new nesting level
        """
        self.set_attribute("nesting", value)


class CodeBlock(ASTNode):
    """
    Represents a code block with optional language specification.
    """

    def __init__(self, code, language, children=None):
        """
        Initialize a CodeBlock node.

        Args:
            code (str): The code content.
            language (str): The programming language of the code.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__(
            "code_block", children, attributes={"code": code, "language": language}
        )

    @property
    def code(self):
        """
        str: The code content.
        """
        return self.attributes.get("code", "")

    @code.setter
    def code(self, value):
        """
        Set the code content.

        Args:
            value (str): The new code content.
        """
        self.set_attribute("code", value)

    @property
    def language(self):
        """
        str: The programming language of the code block.
        """
        return self.attributes.get("language", "")

    @language.setter
    def language(self, value):
        """
        Set the programming language.

        Args:
            value (str): The new language.
        """
        self.set_attribute("language", value)


class InlineCode(ASTNode):
    """
    Represents an inline code span.
    """

    def __init__(self, code, children=None):
        """
        Initialize an InlineCode node.

        Args:
            code (str): The inline code content.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("inline_code", children, attributes={"code": code})

    @property
    def code(self):
        """
        str: The inline code content.
        """
        return self.attributes.get("code", "")

    @code.setter
    def code(self, value):
        """
        Set the inline code content.

        Args:
            value (str): The new code content.
        """
        self.set_attribute("code", value)


class Image(ASTNode):
    """
    Represents an image node with source and alt text.
    """

    def __init__(self, source, alt_text, children=None):
        """
        Initialize an Image node.

        Args:
            source (str): The image source URL or path.
            alt_text (str): The alternative text for the image.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__(
            "image", children, attributes={"source": source, "alt_text": alt_text}
        )

    @property
    def source(self):
        """
        str: The image source.
        """
        return self.attributes.get("source", "")

    @source.setter
    def source(self, value):
        """
        Set the image source.

        Args:
            value (str): The new image source.
        """
        self.set_attribute("source", value)

    @property
    def alt_text(self):
        """
        str: The alternative text for the image.
        """
        return self.attributes.get("alt_text", "")

    @alt_text.setter
    def alt_text(self, value):
        """
        Set the alternative text.

        Args:
            value (str): The new alternative text.
        """
        self.set_attribute("alt_text", value)


class Link(ASTNode):
    """
    Represents a hyperlink node.
    """

    def __init__(self, source, text, children=None):
        """
        Initialize a Link node.

        Args:
            source (str): The URL or link target.
            text (str): The link text.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("link", children, attributes={"source": source, "text": text})

    @property
    def source(self):
        """
        str: The link target.
        """
        return self.attributes.get("source", "")

    @source.setter
    def source(self, value):
        """
        Set the link target.

        Args:
            value (str): The new link target.
        """
        self.set_attribute("source", value)

    @property
    def text(self):
        """
        str: The link text.
        """
        return self.attributes.get("text", "")

    @text.setter
    def text(self, value):
        """
        Set the link text.

        Args:
            value (str): The new link text.
        """
        self.set_attribute("text", value)


class HorizontalRule(ASTNode):
    """
    Represents a horizontal rule (thematic break) in the document.
    """

    def __init__(self, children=None):
        """
        Initialize a HorizontalRule node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("horizontal_rule", children)


class Table(ASTNode):
    """
    Represents a table node.
    """

    def __init__(self, children=None):
        """
        Initialize a Table node.

        Args:
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("table", children)


class TableRow(ASTNode):
    """
    Represents a row in a table, optionally a header row.
    """

    def __init__(self, is_header=False, children=None):
        """
        Initialize a TableRow node.

        Args:
            is_header (bool, optional): Whether the row is a header. Defaults to False.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("table_row", children, attributes={"is_header": is_header})

    @property
    def is_header(self):
        """
        bool: Whether the row is a header row.
        """
        return self.attributes.get("is_header", False)

    @is_header.setter
    def is_header(self, value):
        """
        Set whether the row is a header.

        Args:
            value (bool): True if the row is a header, False otherwise.
        """
        self.set_attribute("is_header", value)


class TableCell(ASTNode):
    """
    Represents a cell in a table with alignment.
    """

    def __init__(self, alignment="left", children=None):
        """
        Initialize a TableCell node.

        Args:
            alignment (str, optional): The cell alignment ("left", "center","right").
                Defaults to "left".
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("table_cell", children, attributes={"alignment": alignment})

    @property
    def alignment(self):
        """
        str: The alignment of the table cell.
        """
        return self.attributes.get("alignment", "left")

    @alignment.setter
    def alignment(self, value):
        """
        Set the alignment of the table cell.

        Args:
            value (str): The new alignment.
        """
        self.set_attribute("alignment", value)


class TaskListItem(ASTNode):
    """
    Represents a task list item with a checked/unchecked state.
    """

    def __init__(self, checked=False, children=None):
        """
        Initialize a TaskListItem node.

        Args:
            checked (bool, optional): Whether the task is checked. Defaults to False.
            children (list, optional): Child nodes. Defaults to None.
        """
        super().__init__("task_list_item", children, attributes={"checked": checked})

    @property
    def checked(self):
        """
        bool: Whether the task is checked.
        """
        return self.attributes.get("checked", False)

    @checked.setter
    def checked(self, value):
        """
        Set the checked state of the task.

        Args:
            value (bool): The new checked state.
        """
        self.set_attribute("checked", value)
