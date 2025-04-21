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
        node.content = node.content.lstrip("#").rstrip("\n")

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

    @process_prenode(NodeType.TEXT)
    def _process_text(self, node: PreNode) -> ast.ASTNode:
        """
        Converts a text PreNode into an AST Text node.

        Args:
            node (PreNode): A PreNode of type TEXT.

        Returns:
            ast.Text: A plain text node for the AST.
        """
        return ast.Text(node.content)

    def to_file(self, ast_root):
        """
        Converts an AST back to a file (not implemented yet).

        Args:
            ast_root (ASTNode): The root of the AST.

        Returns:
            str: Placeholder string for now.
        """
        return "In progress"
