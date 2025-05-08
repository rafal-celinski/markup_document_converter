from src.markup_document_converter.converters.base_converter import BaseConverter
import src.markup_document_converter.ast as ast
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List


class NodeType(Enum):
    HEADING = auto()
    UR_LIST_ITEM = auto()
    OR_LIST_ITEM = auto()
    TASK_LIST_ITEM = auto()
    PARAGRAPH = auto()
    LINE_BREAK = auto()
    TEXT = auto()


@dataclass(order=True)
class PreNode:
    content: str
    node_type: NodeType


def process_prenode(node_type: NodeType) -> Callable:
    """
    Decorator used to register processing functions for specific NodeTypes.

    Args:
        node_type (NodeType): The type of node this function will handle.

    Returns:
        Callable: A decorator function that adds `_node_type` attribute to the handler.
    """

    def decorator(func: Callable) -> Callable:
        func._node_type = node_type
        return func

    return decorator


class MarkdownConverter(BaseConverter):
    def __init__(self) -> None:
        """
        Initializes the MarkdownConverter. Compiles regex patterns and registers
        node processing methods decorated with `@process_prenode`.
        """
        super().__init__()

        self.patterns: dict[NodeType, str] = {
            NodeType.HEADING: r"^(#+)\s.*\n$",
            NodeType.UR_LIST_ITEM: r"^\s*[-*+]\s.*\n$",
            NodeType.OR_LIST_ITEM: r"^\s*\d+\.\s+.*\n$",
            NodeType.LINE_BREAK: r"^\s*$",
            # Keep TEXT at the end so that is it default in case no pattern matches
            NodeType.TEXT: r".*",
        }

        self.inline_pattern = re.compile(
            r"(?P<code>`+)(?P<code_content>.+?)(?P=code)"
            r"|(?P<stars>\*{3,})(?P<stars_content>.+?)(?P=stars)"
            r"|(?P<stars_bold>\*{2})(?P<stars_bold_content>.+?)(?P=stars_bold)"
            r"|(?P<stars_italic>\*)(?P<stars_italic_content>.+?)(?P=stars_italic)"
            r"|(?P<tilde>~{2,})(?P<tilde_content>.+?)(?P=tilde)",
            re.DOTALL,
        )

        self.node_funcs: dict[NodeType, Callable[[PreNode], ast.ASTNode]] = {}

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
        lines = self._get_file_contents(input_file)
        root = ast.Document()

        pre_nodes = self._generate_prenodes(lines)
        pre_nodes = self._group_pre_nodes(pre_nodes)

        for node in pre_nodes:
            handler = self.node_funcs[node.node_type]
            ast_node = handler(node)
            root.add_child(ast_node)

        root = self._group_lists(root)
        return root

    def _group_pre_nodes(self, pre_nodes: List[PreNode]) -> List[PreNode]:
        """
        Groups consecutive TEXT nodes into PARAGRAPH nodes and retains single-line node types.

        Args:
            pre_nodes (List[PreNode]): Flat list of parsed PreNodes.

        Returns:
            List[PreNode]: Grouped PreNodes, ready for processing into AST nodes.
        """
        single_types = [NodeType.HEADING, NodeType.LINE_BREAK]
        grouped = []
        idx = 0
        grouping_node = None

        while idx < len(pre_nodes):
            node = pre_nodes[idx]
            if node.node_type in single_types:
                if grouping_node:
                    grouped.append(grouping_node)
                    grouping_node = None
                grouped.append(node)
            else:
                if not grouping_node:
                    grouping_node = node
                else:
                    if node.node_type == NodeType.TEXT:
                        grouping_node.content += node.content
                    else:
                        grouped.append(grouping_node)
                        grouping_node = node
                if grouping_node and grouping_node.node_type == NodeType.TEXT:
                    grouping_node.node_type = NodeType.PARAGRAPH
            idx += 1

        if grouping_node:
            grouped.append(grouping_node)

        return grouped

    def _group_lists(self, original_root: ast.ASTNode) -> ast.ASTNode:
        """
        Groups list item nodes into nested list structures in the AST.

        Args:
            original_root (ASTNode): Root node with flat children.

        Returns:
            ASTNode: Root node with grouped list structures.
        """
        grouped_root = ast.Document()

        def merger(idx: int, nesting_lvl: int, list_root: ast.ASTNode) -> int:
            curr_list = None
            while idx < len(original_root.children):
                node = original_root.children[idx]
                if node.node_type == "list_item" and node.nesting == nesting_lvl:
                    if curr_list and curr_list.list_type == node.order:
                        curr_list.add_child(node)
                    else:
                        if curr_list:
                            list_root.add_child(curr_list)
                        curr_list = ast.List(list_type=node.order, children=[node])
                    idx += 1
                elif node.node_type == "list_item" and node.nesting < nesting_lvl:
                    if curr_list:
                        list_root.add_child(curr_list)
                    return idx
                elif node.node_type == "list_item" and node.nesting > nesting_lvl:
                    new_list_root = ast.ListItem(order=node.order, nesting=node.nesting)
                    if curr_list:
                        curr_list.add_child(new_list_root)
                        idx = merger(idx, node.nesting, new_list_root)
                    else:
                        idx = merger(idx, node.nesting, list_root)
                else:
                    if curr_list:
                        list_root.add_child(curr_list)
                        curr_list = None
                    list_root.add_child(node)
                    idx += 1
            if curr_list:
                list_root.add_child(curr_list)
            return idx

        merger(0, 0, grouped_root)
        return grouped_root

    def _get_file_contents(self, file_path: str) -> List[str]:
        """
        Reads the file content and ensures it ends with a newline.

        Args:
            file_path (str): Path to the file.

        Returns:
            List[str]: File lines with newlines preserved.
        """
        with open(file_path, "r") as fp:
            text = fp.read()

        if not text.endswith("\n"):
            text += "\n"

        return text.splitlines(keepends=True)

    def _generate_prenodes(self, lines: List[str]) -> List[PreNode]:
        """
        Converts lines of text into PreNodes using pattern matching.

        Args:
            lines (List[str]): Lines from input file.

        Returns:
            List[PreNode]: Generated PreNodes.
        """
        pre_nodes = []
        for line in lines:
            for node_type, pattern in self.patterns.items():
                if re.match(pattern, line):
                    pre_nodes.append(PreNode(content=line, node_type=node_type))
                    break
        return pre_nodes

    def _build_inline_node(
        self, node_class: type[ast.ASTNode], content: str
    ) -> ast.ASTNode:
        """
        Helper function to build an inline node and parse its children.

        Args:
            node_class (type[ASTNode]): Type of the node to create.
            content (str): Inner content to parse.

        Returns:
            ASTNode: Parsed inline node.
        """
        node = node_class()
        for child in self._parse_inline(content):
            node.add_child(child)
        return node

    def _parse_match(self, match: re.Match) -> ast.ASTNode:
        """
        Converts a regex match to the appropriate inline AST node.

        Args:
            match (re.Match): The regex match object.

        Returns:
            ASTNode: Inline-formatted AST node.

        Raises:
            ValueError: If the match doesn't match known inline formats.
        """
        mapping = {
            "code": ast.InlineCode,
            "tilde": ast.Strike,
            "stars_bold": ast.Bold,
            "stars_italic": ast.Italic,
        }

        for group_name, node_class in mapping.items():
            if match.group(group_name):
                if group_name == "code":
                    return node_class(code=match.group("code_content"))
                return self._build_inline_node(
                    node_class, match.group(f"{group_name}_content")
                )

        if match.group("stars"):
            stars = match.group("stars")
            content = match.group("stars_content")
            if len(stars) % 2 == 0:
                return self._build_inline_node(ast.Bold, content)
            else:
                bold_node = ast.Bold()
                italic_node = self._build_inline_node(ast.Italic, content)
                bold_node.add_child(italic_node)
                return bold_node

        raise ValueError("Unrecognized inline match")

    def _parse_inline(self, text: str) -> List[ast.ASTNode]:
        """
        Parses a string with potential inline formatting into a list of AST nodes.

        Args:
            text (str): Input string.

        Returns:
            List[ASTNode]: List of inline-parsed AST nodes.
        """
        if not self.inline_pattern.search(text):
            return [ast.Text(text)]

        children = []
        pos = 0
        while pos < len(text):
            match = self.inline_pattern.search(text, pos)
            if not match:
                children.append(ast.Text(text[pos:]))
                break
            start, end = match.span()
            if start > pos:
                children.append(ast.Text(text[pos:start]))
            children.append(self._parse_match(match))
            pos = end

        return children

    @process_prenode(NodeType.LINE_BREAK)
    def _process_line_break(self, node: PreNode) -> ast.ASTNode:
        """Converts a line break PreNode to a LineBreak AST node."""
        return ast.LineBreak()

    @process_prenode(NodeType.HEADING)
    def _process_heading(self, node: PreNode) -> ast.ASTNode:
        """Parses heading syntax and returns a Heading AST node."""
        heading_level = len(re.findall(r"#+", node.content)[0])
        node.content = node.content.lstrip("# ").rstrip("\n")

        heading = ast.Heading(level=heading_level)
        for child in self._parse_inline(node.content):
            heading.add_child(child)
        return heading

    @process_prenode(NodeType.UR_LIST_ITEM)
    def _process_ur_list_item(self, node: PreNode) -> ast.ASTNode:
        """Parses unordered list item into ListItem AST node."""
        nesting_level = len(re.findall(r"(\s*)[-*+]", node.content)[0])
        node.content = node.content[nesting_level + 2 :]
        list_item = ast.ListItem(order="unordered", nesting=nesting_level)
        for child in self._parse_inline(node.content):
            list_item.add_child(child)
        return list_item

    @process_prenode(NodeType.OR_LIST_ITEM)
    def _process_or_list_item(self, node: PreNode) -> ast.ASTNode:
        """Parses ordered list item into ListItem AST node"""
        nesting_level = len(re.findall(r"(\s*)\d*\.\s", node.content)[0])
        num_len = len(re.findall(r"\s*(\d*\.\s)", node.content)[0])
        node.content = node.content[nesting_level + num_len :]
        list_item = ast.ListItem(order="ordered", nesting=nesting_level)
        for child in self._parse_inline(node.content):
            list_item.add_child(child)
        return list_item

    @process_prenode(NodeType.PARAGRAPH)
    def _process_paragraph(self, node: PreNode) -> ast.ASTNode:
        """
        Parses a paragraph and returns a Paragraph AST node.

        Args:
            node (PreNode): A PreNode containing paragraph text.

        Returns:
            Paragraph: A Paragraph AST node with parsed inline children.
        """
        paragraph_node = ast.Paragraph()
        for inline_child in self._parse_inline(node.content):
            paragraph_node.add_child(inline_child)
        return paragraph_node

    def to_file(self, ast_root: ast.ASTNode) -> str:
        """
        Converts the AST back to a file (not implemented).

        Args:
            ast_root (ASTNode): Root of the AST.

        Returns:
            str: Placeholder string.
        """
        return "In progress"
