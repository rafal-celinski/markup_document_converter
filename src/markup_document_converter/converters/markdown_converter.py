from src.markup_document_converter.converters.base_converter import BaseConverter
import src.markup_document_converter.ast as ast
import re
from dataclasses import dataclass
from enum import Enum, auto


class NodeType(Enum):
    HEADING = auto()
    LIST_ITEM = auto()
    PARAGRAPH = auto()


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
            NodeType.LIST_ITEM: r"^(?P<indent>\s*)-\s.*(?:\n(?!\s*[-*+]|\s*\n).*)*",
        }

        self.inline_pattern = re.compile(
            r"(?P<code>`+)(?P<code_content>.+?)(?P=code)"
            r"|(?P<stars>\*{3,})(?P<stars_content>.+?)(?P=stars)"
            r"|(?P<stars_bold>\*{2})(?P<stars_bold_content>.+?)(?P=stars_bold)"
            r"|(?P<stars_italic>\*)(?P<stars_italic_content>.+?)(?P=stars_italic)"
            r"|(?P<tilde>~{2,})(?P<tilde_content>.+?)(?P=tilde)",
            re.DOTALL,
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
        pre_nodes = []
        for name in self.patterns:
            pattern = re.compile(self.patterns[name], re.MULTILINE)
            for match in pattern.finditer(text):
                pre_nodes.append(PreNode(match.start(), match.group(), name))

        pre_nodes.sort()

        filled_nodes = []
        current_pos = 0
        for node in pre_nodes:
            if current_pos < node.start_idx:
                unmatched_text = text[current_pos : node.start_idx]
                paragraphs = re.split(r"\n\s*\n", unmatched_text)
                offset = current_pos
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        filled_nodes.append(PreNode(offset, para, NodeType.PARAGRAPH))
                    offset += len(para) + 2
            filled_nodes.append(node)
            current_pos = node.start_idx + len(node.content)

        if current_pos < len(text):
            unmatched_text = text[current_pos:]
            paragraphs = re.split(r"\n\s*\n", unmatched_text)
            offset = current_pos
            for para in paragraphs:
                para = para.strip()
                if para:
                    filled_nodes.append(PreNode(offset, para, NodeType.PARAGRAPH))
                offset += len(para) + 2

        return sorted(filled_nodes, key=lambda n: n.start_idx)

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
        for child in self._parse_inline(node.content):
            heading.add_child(child)
        return heading

    ## TODO: Correct striping and level detection
    @process_prenode(NodeType.LIST_ITEM)
    def _process_list_item(self, node: PreNode) -> ast.ASTNode:
        """
        Converts a list item PreNode into an AST ListItem node.

        Args:
            node (PreNode): A PreNode of type LIST_ITEM.

        Returns:
            ast.ListItem: A list item node for the AST.
        """
        node.content = node.content.lstrip(" -")

        list_item = ast.ListItem(order="unordered")
        for child in self._parse_inline(node.content):
            list_item.add_child(child)
        return list_item

    def _build_inline_node(
        self, node_class: type[ast.ASTNode], content: str
    ) -> ast.ASTNode:
        """
        Helper function to create an inline AST node and parse its children from content.

        Args:
            node_class (type[ast.ASTNode]): Class of the AST node to create (Bold, Italic, Strike, etc.).
            content (str): Inner content to parse.

        Returns:
            ast.ASTNode: The created and populated AST node.
        """
        parsed = self._parse_inline(content)

        node = node_class()
        for child in parsed:
            node.add_child(child)
        return node

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
                content = match.group(f"{group_name}_content")
                return self._build_inline_node(node_class, content)

        if match.group("stars"):
            stars = match.group("stars")
            content = match.group("stars_content")
            star_count = len(stars)

            if star_count % 2 == 0:
                return self._build_inline_node(ast.Bold, content)
            else:
                bold_node = ast.Bold()
                italic_node = self._build_inline_node(ast.Italic, content)
                bold_node.add_child(italic_node)
                return bold_node

        raise ValueError("Unrecognized inline match")

    def _parse_inline(self, text: str) -> list[ast.ASTNode]:
        """
        Parses text, possibly containing multiple inline markup elements,
        and returns a list of AST nodes representing the parsed inline elements.

        Args:
            text (str): The full text containing potential inline formatting.

        Returns:
            list[ASTNode]: A list of AST nodes parsed from the text.
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

    @process_prenode(NodeType.PARAGRAPH)
    def _process_paragraph(self, node: PreNode) -> ast.ASTNode:
        """
        Parses parahgraph for inline formatting like bold, italic, strike, code,

        Args:
            node (PreNode): A PreNode of type PARAGRAPH.

        Returns:
            Node (Paragraph): A Paragraphed with parsed inline text
        """

        paragraph_node = ast.Paragraph()
        for inline_child in self._parse_inline(node.content):
            paragraph_node.add_child(inline_child)

        return paragraph_node

    def to_file(self, ast_root):
        """
        Converts an AST back to a file (not implemented yet).

        Args:
            ast_root (ASTNode): The root of the AST.

        Returns:
            str: Placeholder string for now.
        """
        return "In progress"
