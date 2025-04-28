from src.markup_document_converter.converters.base_converter import BaseConverter
import src.markup_document_converter.ast as ast
import re
from dataclasses import dataclass
from enum import Enum, auto


class NodeType(Enum):
    HEADING = auto()
    LIST_ITEM = auto()
    TEXT = auto()


@dataclass(order=True)
class PreNode:
    start_idx: int
    content: str
    node_type: NodeType


def process_prenode(node_type: NodeType):
    """
    Decorator used to register processing functions for specific NodeTypes.

    Args:
        node_type (NodeType): The type of node this function will handle.

    Returns:
        Callable: A decorator function that adds `_node_type` attribute to the handler.
    """

    def decorator(func):
        func._node_type = node_type
        return func

    return decorator


class MarkdownConverter(BaseConverter):
    def __init__(self):
        """
        Initializes the MarkdownConverter. Compiles regex patterns and registers
        node processing methods decorated with `@process_prenode`.
        """
        super().__init__()

        self.patterns = {
            NodeType.HEADING: r"^(#+)\s.*\n",
            NodeType.LIST_ITEM: r"^(\s*)-\s.*\n",
        }

        self.inline_pattern = re.compile(
            r"(?P<code>`[^`]+?`)"
            r"|(?P<bolditalic>\*\*\*[^*]+?\*\*\*)"
            r"|(?P<bold>\*\*[^*]+?\*\*)"
            r"|(?P<italic>(\*[^*]+?\*)|(_[^_]+?_))"
            r"|(?P<strike>~~[^~]+?~~)"
        )

        self.node_funcs = {}

        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_node_type"):
                self.node_funcs[method._node_type] = method

    def to_AST(self, input_file: str) -> ast.ASTNode:
        """
        Parses a markup file and converts it to an AST.

        Args:
            input_file (str): Path to the markup file.

        Returns:
            ASTNode: Parsed AST tree representing the structure of the document.
        """
        text = self._get_file_contents(input_file)
        root = ast.Document()
        pre_nodes = self._generate_prenodes(text)

        for node in pre_nodes:
            handler = self.node_funcs[node.node_type]
            root.add_child(handler(node))

        return root

    def _get_file_contents(self, file_path: str) -> str:
        """
        Reads the file content and ensures it ends with a newline.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: File contents as a single string.
        """
        with open(file_path, "r") as fp:
            text = fp.read()

        if text[-1] != "\n":
            text += "\n"

        return text

    def _generate_prenodes(self, text: str) -> list[PreNode]:
        """
        Creates a list of PreNodes, representing different markup structures
        found in the raw text using regex patterns. Also fills gaps with TEXT nodes.

        Args:
            text (str): Raw content of a file.

        Returns:
            list[PreNode]: Sorted list of PreNodes covering both matched and unmatched text.
        """
        pre_nodes = []
        for name in self.patterns:
            pattern = re.compile(self.patterns[name], re.MULTILINE)
            for match in pattern.finditer(text):
                pre_nodes.append(PreNode(match.start(), match.group(), name))

        pre_nodes.sort()

        # Create text nodes for gaps
        filled_nodes = []
        current_pos = 0
        for node in pre_nodes:
            if current_pos < node.start_idx:
                unmatched_text = text[current_pos : node.start_idx]
                filled_nodes.append(PreNode(current_pos, unmatched_text, NodeType.TEXT))
            filled_nodes.append(node)
            current_pos = node.start_idx + len(node.content)

        if current_pos < len(text):
            tail_text = text[current_pos:]
            filled_nodes.append(PreNode(current_pos, tail_text, NodeType.TEXT))

        return filled_nodes

    @process_prenode(NodeType.HEADING)
    def _process_heading(self, node: PreNode) -> ast.ASTNode:
        """
        Converts a heading PreNode into an AST Heading node.

        Args:
            node (PreNode): A PreNode of type HEADING.

        Returns:
            ast.Heading: A heading node for the AST.
        """
        heading_level = len(re.findall(r"#+", node.content)[0])
        node.content = node.content.lstrip("# ").rstrip("\n")

        heading = ast.Heading(level=heading_level)
        heading.add_child(self._process_text(node))
        return heading

    @process_prenode(NodeType.LIST_ITEM)
    def _process_list_item(self, node: PreNode) -> ast.ASTNode:
        """
        Converts a list item PreNode into an AST ListItem node.

        Args:
            node (PreNode): A PreNode of type LIST_ITEM.

        Returns:
            ast.ListItem: A list item node for the AST.
        """
        node.content = node.content.lstrip(" -").rstrip("\n")

        list_item = ast.ListItem(order="unordered")
        list_item.add_child(self._process_text(node))
        return list_item

    def _strip_markers(self, text: str, left: int, right: int) -> str:
        """
        Removes a fixed number of characters from both sides of the text.
        Typically used to strip markup symbols like **, *, ~~, or `.

        Args:
            text (str): The input text containing markers.
            left (int): Number of characters to strip from the left.
            right (int): Number of characters to strip from the right.

        Returns:
            str: Text with markers removed.
        """
        if not text:
            return ""
        return text[left:-right]

    def _parse_match(self, match: re.Match) -> ast.ASTNode:
        """
        Parses a single regex match corresponding to inline formatting,
        and constructs the appropriate AST node (bold, italic, code, strike).

        Args:
            match (re.Match): A regex match containing inline markup.

        Returns:
            ast.ASTNode: A parsed AST node representing the matched formatting.

        Raises:
            ValueError: If the match does not correspond to any recognized formatting.
        """
        if match.group("code"):
            return ast.InlineCode(code=self._strip_markers(match.group("code"), 1, 1))
        if match.group("bolditalic"):
            bold_node = ast.Bold()
            italic_node = ast.Italic()
            inner_text = self._strip_markers(match.group("bolditalic"), 3, 3)
            italic_node.add_child(self._parse_fragment(inner_text))
            bold_node.add_child(italic_node)
            return bold_node
        if match.group("bold"):
            bold_node = ast.Bold()
            inner_text = self._strip_markers(match.group("bold"), 2, 2)
            bold_node.add_child(self._parse_fragment(inner_text))
            return bold_node
        if match.group("strike"):
            strike_node = ast.Strike()
            inner_text = self._strip_markers(match.group("strike"), 2, 2)
            strike_node.add_child(self._parse_fragment(inner_text))
            return strike_node
        if match.group("italic"):
            italic_node = ast.Italic()
            inner_text = self._strip_markers(match.group("italic"), 1, 1)
            italic_node.add_child(self._parse_fragment(inner_text))
            return italic_node
        raise ValueError("Unrecognized inline match")

    def _parse_fragment(self, text: str) -> ast.ASTNode:
        """
        Parses a text fragment to determine whether it contains inline formatting.
        If formatting is detected, processes it recursively.

        Args:
            text (str): The text fragment to parse.

        Returns:
            ast.ASTNode: Either a plain Text node or a parsed Inline subtree.
        """
        if not self.inline_pattern.search(text):
            return ast.Text(text)
        return self._parse_inline(text)

    def _parse_inline(self, text: str) -> ast.ASTNode:
        """
        Parses text, possibly containing multiple inline markup elements,
        and constructs a hierarchical Inline AST subtree.

        Args:
            text (str): The full text containing potential inline formatting.

        Returns:
            ast.ASTNode: A composite AST node representing all inline elements.
        """
        if not any(c in text for c in ["*", "_", "~", "`"]):
            return ast.Text(text)

        matches = list(self.inline_pattern.finditer(text))
        if not matches:
            return ast.Text(text)

        root = ast.Inline()
        last_idx = 0
        for match in matches:
            start, end = match.span()

            if last_idx < start:
                fragment = text[last_idx:start]
                root.add_child(self._parse_fragment(fragment))

            root.add_child(self._parse_match(match))

            last_idx = end

        if last_idx < len(text):
            fragment = text[last_idx:]
            root.add_child(self._parse_fragment(fragment))

        if len(root.children) == 1:
            return root.children[0]
        return root

    @process_prenode(NodeType.TEXT)
    def _process_text(self, node: PreNode) -> ast.ASTNode:
        """
        Parses plain text for inline formatting like bold, italic, strike, code,
        and returns a composite AST node

        Args:
            node (PreNode): A PreNode of type TEXT.

        Returns:
            ast.Inline: An AST subtree containing parsed TEXT.
        """
        return self._parse_inline(node.content)

    def to_file(self, ast_root):
        """
        Converts an AST back to a file (not implemented yet).

        Args:
            ast_root (ASTNode): The root of the AST.

        Returns:
            str: Placeholder string for now.
        """
        return "In progress"
