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


class Text(ASTNode):
    def __init__(self, text):
        super().__init__("text", children=[], attributes={"text": text})

    @property
    def text(self):
        return self.attributes.get("text", "")

    @text.setter
    def text(self, value):
        self.set_attribute("text", value)
