class ASTNode:
    def __init__(self, node_type: str, children: list = None, attributes: dict = None):
        self._node_type = node_type
        self._children = children or []
        self._attributes = attributes or {}

    def set_attribute(self, key: str, value):
        self._attributes[key] = value

    @property
    def attributes(self):
        return self._attributes

    def add_child(self, child):
        self._children.append(child)

    @property
    def children(self):
        return self._children


class Document(ASTNode):
    def __init__(self, children=None):
        super().__init__("document", children)


class Heading(ASTNode):
    def __init__(self, level, children=None):
        super().__init__("header", children, attributes={"level": level})

    @property
    def level(self):
        return self.attributes.get("level", 1)

    @level.setter
    def level(self, value):
        self.set_attribute("level", value)


class Bold(ASTNode):
    def __init__(self, children=None):
        super().__init__("bold", children)


class Italic(ASTNode):
    def __init__(self, children=None):
        super().__init__("italic", children)


class Strike(ASTNode):
    def __init__(self, children=None):
        super().__init__("strike", children)


class Text(ASTNode):
    def __init__(self, text):
        super().__init__("text", children=[], attributes={"text": text})

    @property
    def text(self):
        return self.attributes.get("text", "")

    @text.setter
    def text(self, value):
        self.set_attribute("text", value)


class Paragraph(ASTNode):
    def __init__(self, children=None):
        super().__init__("paragraph", children)


class LineBreak(ASTNode):
    def __init__(self, children=None):
        super().__init__("line_break", children)


class Blockquote(ASTNode):
    def __init__(self, children=None):
        super().__init__("blockquote", children)


class List(ASTNode):
    def __init__(self, list_type):
        super().__init__("list", children=[], attributes={"list_type": list_type})

    @property
    def list_type(self):
        return self.attributes.get("list_type", "")

    @list_type.setter
    def list_type(self, value):
        self.set_attribute("list_type", value)


class ListItem(ASTNode):
    def __init__(self, order):
        super().__init__("list_item", children=[], attributes={"order": order})

    @property
    def order(self):
        return self.attributes.get("order", "")

    @order.setter
    def order(self, value):
        self.set_attribute("order", value)


class CodeBlock(ASTNode):
    def __init__(self, code, language=None):
        super().__init__("code_block", children=[], 
                         attributes={"code": code, "language": language})

    @property
    def code(self):
        return self.attributes.get("code", "")

    @code.setter
    def code(self, value):
        self.set_attribute("code", value)

    @property
    def language(self):
        return self.attributes.get("language", "")

    @language.setter
    def language(self, value):
        self.set_attribute("language", value)


class Image(ASTNode):
    def __init__(self, source, alt_text):
        super().__init__("image", children=[], attributes={"source": source, "alt_text": alt_text})

    @property
    def source(self):
        return self.attributes.get("source", "")

    @source.setter
    def source(self, value):
        self.set_attribute("source", value)

    @property
    def alt_text(self):
        return self.attributes.get("alt_text", "")

    @alt_text.setter
    def alt_text(self, value):
        self.set_attribute("alt_text", value)


class Link(ASTNode):
    def __init__(self, source, text):
        super().__init__("link", children=[], attributes={"source": source, "text": text})

    @property
    def source(self):
        return self.attributes.get("source", "")

    @source.setter
    def source(self, value):
        self.set_attribute("source", value)

    @property
    def text(self):
        return self.attributes.get("text", "")

    @text.setter
    def text(self, value):
        self.set_attribute("text", value)


class HorizontalRule(ASTNode):
    def __init__(self):
        super().__init__("horizontal_rule", children=[])


class Table(ASTNode):
    def __init__(self, children=None):
        super().__init__("table", children)


class TableRow(ASTNode):
    def __init__(self, children=None, is_header=False):
        super().__init__("table_row", children, attributes={"is_header": is_header})

    @property
    def is_header(self):
        return self.attributes.get("is_header", False)

    @is_header.setter
    def is_header(self, value):
        self.set_attribute("is_header", value)


class TableCell(ASTNode):
    def __init__(self, children=None, alignment=None):
        super().__init__("table_cell", children, attributes={"alignment": alignment})

    @property
    def alignment(self):
        return self.attributes.get("alignment", "left")

    @alignment.setter
    def alignment(self, value):
        self.set_attribute("alignment", value)


class TaskListItem(ASTNode):
    def __init__(self, children=None, checked=False):
        super().__init__("task_list_item", children, attributes={"checked": checked})

    @property
    def checked(self):
        return self.attributes.get("checked", False)

    @checked.setter
    def checked(self, value):
        self.set_attribute("checked", value)
