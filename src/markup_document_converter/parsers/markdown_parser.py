from markup_document_converter.parsers.base_parser import BaseParser
from markup_document_converter.registry import register_parser
import markup_document_converter.ast_tree as ast_tree
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, List


class NodeType(Enum):
    """
    Enumeration of all possible node types detected during Markdown preprocessing.
    """

    HEADING = auto()
    UR_LIST_ITEM = auto()
    OR_LIST_ITEM = auto()
    TASK_LIST_ITEM = auto()
    PARAGRAPH = auto()
    LINE_BREAK = auto()
    TEXT = auto()
    LINK = auto()
    IMAGE = auto()
    BLOCKQOUTE = auto()
    CODE_BORDER = auto()
    CODE_BLOCK = auto()
    TABLE_ROW = auto()
    TABLE_BORDER = auto()
    TABLE = auto()
    HORIZONTAL_RULE = auto()
    LIST = auto()
    BLOCKQOUTE_GROUP = auto()


def print_pre_node(node, indent=0):
    pad = "  " * indent
    print(f"{pad}- {node.node_type.name}: '{node.content.strip()}'")
    for child in node.pre_children:
        print_pre_node(child, indent + 1)


def get_text_content(node):
    """Recursively gets text content from a node."""
    if node.node_type == NodeType.TEXT:
        return node.content.strip()
    return " ".join(get_text_content(child) for child in node.pre_children)


@dataclass(order=True)
class PreNode:
    """
    Represents a pre-processed node used for intermediate parsing before final AST conversion.

    Attributes:
        content (str): The raw content of the node.
        node_type (NodeType): The type of this node.
        pre_children (list): A list of child PreNodes.
    """

    node_type: NodeType
    content: str = field(default_factory=str)
    pre_children: list = field(default_factory=list)


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


@register_parser("markdown", "md")
class MarkdownParser(BaseParser):
    """
    Parser for converting Markdown text into an abstract syntax tree (AST).
    """

    def __init__(self) -> None:
        """
        Initializes the MarkdownConverter. Compiles regex patterns and registers
        node processing methods decorated with `@process_prenode`.
        """
        super().__init__()

        self.patterns: dict[NodeType, str] = {
            NodeType.HEADING: r"^(#+)\s.*\n$",
            NodeType.HORIZONTAL_RULE: r"^\s*([*\-_])(?:\s*\1){2,}\s*\n$",
            # TASK_LIST_ITEM must be checked first because this type is subset of other list items
            NodeType.TASK_LIST_ITEM: r"^\s*([-*+]|\d+\.)\s+\[( |x|X)\]\s+.*\n$",
            NodeType.UR_LIST_ITEM: r"^\s*[-*+]\s.*\n$",
            NodeType.OR_LIST_ITEM: r"^\s*\d+\.\s+.*\n$",
            NodeType.LINE_BREAK: r"^\s*$",
            NodeType.BLOCKQOUTE: r"^\s*>+.*\n$",
            NodeType.CODE_BORDER: r"^\s*```.*\n$",
            NodeType.TABLE_BORDER: r"^\|?(\s*:?\s*-+:?\s*\|)*\s*:?\s*-+:?\s*\|?\s*\n$",
            NodeType.TABLE_ROW: r"^\|?(.*\|)+.*\|?\n$",
            # Keep TEXT at the end so that is it default in case no pattern matches
            NodeType.TEXT: r".*",
        }

        self.inline_pattern = re.compile(
            r"(?P<code>`+)(?P<code_content>.+?)(?P=code)"
            r"|(?P<stars>\*{3,})(?P<stars_content>.+?)(?P=stars)"
            r"|(?P<stars_bold>\*{2})(?P<stars_bold_content>.+?)(?P=stars_bold)"
            r"|(?P<stars_italic>\*)(?P<stars_italic_content>.+?)(?P=stars_italic)"
            r"|(?P<tilde>~{2,})(?P<tilde_content>.+?)(?P=tilde)"
            r"|!\[(?P<image_alt>[^\]]*)\]\((?P<image_url>[^)]+)\)"
            r"|\[(?P<link_text>[^\]]+)\]\((?P<link_url>[^)]+)\)",
            re.DOTALL,
        )

        self.node_funcs: dict[NodeType, Callable[[PreNode], ast_tree.ASTNode]] = {}

        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_node_type"):
                self.node_funcs[method._node_type] = method

    def to_AST(self, content: str) -> ast_tree.ASTNode:
        """
        Parses markdown content and converts it to an AST.

        Args:
            content (str): Full markdown content as a string.

        Returns:
            ASTNode: Parsed AST document.
        """
        lines = content.splitlines(keepends=True)
        root = ast_tree.Document()

        pre_nodes = self.generate_prenodes(lines)
        pre_nodes = self.group_pre_nodes(pre_nodes)

        for node in pre_nodes:
            handler = self.node_funcs[node.node_type]
            ast_node = handler(node)
            root.add_child(ast_node)

        return root

    def group_pre_nodes(self, pre_nodes: List[PreNode]) -> List[PreNode]:
        """
        Groups consecutive TEXT nodes into PARAGRAPH nodes and retains single-line node types.

        Args:
            pre_nodes (List[PreNode]): Flat list of parsed PreNodes.

        Returns:
            List[PreNode]: Grouped PreNodes, ready for processing into AST nodes.
        """

        def group_blockqoutes(pre_nodes: list[PreNode]):
            """
            Groups nested blockquotes into hierarchical structures.

            Args:
                nodes (list[PreNode]): Flat list of PreNodes.

            Returns:
                list[PreNode]: Transformed list with nested blockquote structure.
            """

            def merger(
                idx: int,
                p_nodes: list[PreNode],
                curr_indent: int,
                root_blockqoute: PreNode,
            ):
                while idx < len(p_nodes):
                    p_node = p_nodes[idx]
                    if p_node.node_type == NodeType.TEXT:
                        root_blockqoute.pre_children.append(p_node)
                        idx += 1
                    elif p_node.node_type == NodeType.BLOCKQOUTE:
                        blockqoute_indent = len(re.findall(r">+", p_node.content)[0])
                        if blockqoute_indent == curr_indent:
                            p_node.node_type = NodeType.TEXT
                            root_blockqoute.pre_children.append(p_node)
                            idx += 1
                        elif blockqoute_indent > curr_indent:
                            new_blockqoute = PreNode(node_type=NodeType.BLOCKQOUTE)
                            root_blockqoute.pre_children.append(new_blockqoute)
                            idx = merger(idx, p_nodes, curr_indent + 1, new_blockqoute)
                        else:
                            return idx
                return idx

            grouped = []
            grouping_node = None

            for p_node in pre_nodes:
                is_blockqoute = p_node.node_type == NodeType.BLOCKQOUTE
                is_text = p_node.node_type == NodeType.TEXT
                if is_blockqoute and not grouping_node:
                    grouping_node = PreNode(
                        node_type=NodeType.BLOCKQOUTE_GROUP, pre_children=[p_node]
                    )
                elif (is_blockqoute or is_text) and grouping_node:
                    grouping_node.pre_children.append(p_node)
                elif not (is_blockqoute or is_text) and grouping_node:
                    grouped.append(grouping_node)
                    grouping_node = None
                    grouped.append(p_node)
                else:
                    grouped.append(p_node)

            if grouping_node:
                grouped.append(grouping_node)

            new_grouped = []

            for p_node in grouped:
                if p_node.node_type == NodeType.BLOCKQOUTE_GROUP:
                    children = p_node.pre_children
                    p_node = PreNode(node_type=NodeType.BLOCKQOUTE)
                    merger(0, children, 1, p_node)
                new_grouped.append(p_node)

            return new_grouped

        def group_lists(pre_nodes: list[PreNode]):
            """
            Groups list items into list structures based on nesting level.

            Args:
                nodes (list[PreNode]): Flat list of PreNodes.

            Returns:
                list[PreNode]: Transformed list with list structure.
            """

            def merger(
                idx: int, nesting_lvl: int, list_root: PreNode, p_nodes: list[PreNode]
            ) -> int:
                list_node = None
                list_type = None
                bucket = None
                while idx < len(p_nodes):
                    p_node = p_nodes[idx]
                    if p_node.node_type in list_element_types:
                        curr_nesting = (
                            len(p_node.pre_children[0].content)
                            - len(p_node.pre_children[0].content.lstrip())
                        ) // 2
                        if curr_nesting == nesting_lvl:
                            if not list_type:
                                list_type = p_node.node_type
                                list_node = PreNode(node_type=NodeType.LIST)
                                list_node.pre_children.append(p_node)
                            elif list_type and list_type == p_node.node_type:
                                list_node.pre_children.append(p_node)
                            elif list_type and list_type != p_node.node_type:
                                if nesting_lvl == 0:
                                    list_root.append(list_node)
                                else:
                                    list_root.pre_children.append(list_node)
                                list_node = PreNode(node_type=NodeType.LIST)
                                list_node.pre_children.append(p_node)
                                list_type = p_node.node_type
                            idx += 1
                        elif curr_nesting > nesting_lvl:
                            if not list_node:
                                bucket = PreNode(node_type=NodeType.UR_LIST_ITEM)
                                list_root.pre_children.append(bucket)
                                idx = merger(idx, nesting_lvl + 1, bucket, p_nodes)
                            else:
                                idx = merger(
                                    idx,
                                    nesting_lvl + 1,
                                    list_node.pre_children[-1],
                                    p_nodes,
                                )
                        elif curr_nesting < nesting_lvl:
                            if list_node is not None:
                                list_root.pre_children.append(list_node)
                            return idx
                    else:
                        if list_node:
                            if nesting_lvl == 0:
                                list_root.append(list_node)
                                list_root.append(p_node)
                            else:
                                list_root.pre_children.append(list_node)
                                return idx
                            list_type = None
                            list_node = None
                        else:
                            list_root.append(p_node)

                        idx += 1
                if list_type:
                    if nesting_lvl == 0:
                        list_root.append(list_node)
                    else:
                        if list_node is not None:
                            list_root.pre_children.append(list_node)
                    return idx
                return idx

            list_element_types = [
                NodeType.OR_LIST_ITEM,
                NodeType.UR_LIST_ITEM,
                NodeType.TASK_LIST_ITEM,
            ]

            grouped = []
            grouping_node = None

            for p_node in pre_nodes:
                if p_node.node_type == NodeType.TEXT:
                    if grouping_node:
                        grouping_node.pre_children.append(p_node)
                    else:
                        grouped.append(p_node)
                elif p_node.node_type in list_element_types:
                    p_node.pre_children = [
                        PreNode(node_type=NodeType.TEXT, content=p_node.content)
                    ]
                    p_node.content = ""
                    if grouping_node:
                        grouped.append(grouping_node)
                    grouping_node = p_node
                else:
                    if grouping_node:
                        grouped.append(grouping_node)
                    grouping_node = None
                    grouped.append(p_node)

            if grouping_node:
                grouped.append(grouping_node)

            new_grouped = []
            merger(0, 0, new_grouped, grouped)

            return new_grouped

        def group_code_blocks(pre_nodes: list[PreNode]):
            """
            Groups contents of code blocks into structures.

            Args:
                nodes (list[PreNode]): Flat list of PreNodes.

            Returns:
                list[PreNode]: Transformed list with code blocks structure.
            """
            grouped = []
            grouping_node = None

            for node in pre_nodes:
                node_is_border = node.node_type == NodeType.CODE_BORDER
                if node_is_border and not grouping_node:
                    grouping_node = PreNode(
                        content=node.content, node_type=NodeType.CODE_BLOCK
                    )
                elif node_is_border and grouping_node:
                    if node.content.lstrip().rstrip() == "```":
                        grouped.append(grouping_node)
                        grouping_node = None
                    else:
                        grouping_node.content += node.content
                elif not node_is_border and not grouping_node:
                    grouped.append(node)
                else:
                    grouping_node.content += node.content
            if grouping_node:
                grouped.append(grouping_node)

            return grouped

        def group_table_rows(pre_nodes: list[PreNode]):
            """
            Groups contents of tables into structures.

            Args:
                nodes (list[PreNode]): Flat list of PreNodes.

            Returns:
                list[PreNode]: Transformed list with full tables structure.
            """
            idx = 0
            grouped = []
            grouping_node = None
            while idx < len(pre_nodes):
                p_node = pre_nodes[idx]
                is_table_row = p_node.node_type == NodeType.TABLE_ROW
                is_table_border = p_node.node_type == NodeType.TABLE_BORDER
                if (is_table_row or is_table_border) and not grouping_node:
                    if (
                        idx + 1 < len(pre_nodes)
                        and pre_nodes[idx + 1].node_type == NodeType.TABLE_BORDER
                    ):
                        grouping_node = PreNode(
                            content=p_node.content, node_type=NodeType.TABLE
                        )
                    else:
                        p_node.node_type = NodeType.TEXT
                        grouped.append(p_node)
                elif (is_table_row or is_table_border) and grouping_node:
                    grouping_node.content += p_node.content
                elif grouping_node:
                    grouped.append(grouping_node)
                    grouping_node = None
                    grouped.append(p_node)
                elif not grouping_node:
                    grouped.append(p_node)
                idx += 1
            if grouping_node:
                grouped.append(grouping_node)
            return grouped

        def group_paragraphs(pre_nodes):
            """
            Groups rest of TEXT pre_nodes into paragraphs.

            Args:
                nodes (list[PreNode]): Flat list of PreNodes.

            Returns:
                list[PreNode]: Transformed list with paragraph structure.
            """
            grouped = []
            grouping_node = None
            for p_node in pre_nodes:
                if p_node.node_type == NodeType.TEXT and not grouping_node:
                    grouping_node = PreNode(NodeType.PARAGRAPH)
                    grouping_node.pre_children.append(p_node)
                elif p_node.node_type == NodeType.TEXT and grouping_node:
                    grouping_node.pre_children.append(p_node)
                else:
                    if grouping_node:
                        grouped.append(grouping_node)
                        grouping_node = None
                    grouped.append(p_node)
            if grouping_node:
                grouped.append(grouping_node)

            return grouped

        post_change_incorrect_table_rows = group_table_rows(pre_nodes)
        post_blockqoutes = group_blockqoutes(post_change_incorrect_table_rows)
        post_code_blocks = group_code_blocks(post_blockqoutes)
        post_lists = group_lists(post_code_blocks)
        post_paragraphs = group_paragraphs(post_lists)
        return post_paragraphs

    def generate_prenodes(self, lines: List[str]) -> List[PreNode]:
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

    def build_inline_node(
        self, node_class: type[ast_tree.ASTNode], content: str
    ) -> ast_tree.ASTNode:
        """
        Helper function to build an inline node and parse its children.

        Args:
            node_class (type[ASTNode]): Type of the node to create.
            content (str): Inner content to parse.

        Returns:
            ASTNode: Parsed inline node.
        """
        node = node_class()
        for child in self.parse_inline(content):
            node.add_child(child)
        return node

    def parse_match(self, match: re.Match) -> ast_tree.ASTNode:
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
            "code": ast_tree.InlineCode,
            "tilde": ast_tree.Strike,
            "stars_bold": ast_tree.Bold,
            "stars_italic": ast_tree.Italic,
        }

        for group_name, node_class in mapping.items():
            if match.group(group_name):
                if group_name == "code":
                    return node_class(code=match.group("code_content"))
                return self.build_inline_node(
                    node_class, match.group(f"{group_name}_content")
                )

        if match.group("stars"):
            stars = match.group("stars")
            content = match.group("stars_content")
            if len(stars) % 2 == 0:
                return self.build_inline_node(ast_tree.Bold, content)
            else:
                bold_node = ast_tree.Bold()
                italic_node = self.build_inline_node(ast_tree.Italic, content)
                bold_node.add_child(italic_node)
                return bold_node

        if match.group("link_text") and match.group("link_url"):
            text = match.group("link_text")
            url = match.group("link_url")
            link_node = ast_tree.Link(source=url)
            for child in self.parse_inline(text):
                link_node.add_child(child)
            return link_node

        if match.group("image_alt") and match.group("image_url"):
            alt = match.group("image_alt")
            src = match.group("image_url")
            return ast_tree.Image(source=src, alt_text=alt)

        raise ValueError("Unrecognized inline match")

    def parse_inline(self, text: str) -> List[ast_tree.ASTNode]:
        """
        Parses a string with potential inline formatting into a list of AST nodes.

        Args:
            text (str): Input string.

        Returns:
            List[ASTNode]: List of inline-parsed AST nodes.
        """
        if not self.inline_pattern.search(text):
            return [ast_tree.Text(text)]

        children = []
        pos = 0
        while pos < len(text):
            match = self.inline_pattern.search(text, pos)
            if not match:
                children.append(ast_tree.Text(text[pos:]))
                break
            start, end = match.span()
            if start > pos:
                children.append(ast_tree.Text(text[pos:start]))
            children.append(self.parse_match(match))
            pos = end

        return children

    @process_prenode(NodeType.LINE_BREAK)
    def process_line_break(self, node: PreNode) -> ast_tree.ASTNode:
        """Converts a line break PreNode to a LineBreak AST node.
        Args:
            node (PreNode): A line_break PreNode - always empty.

        Returns:
            ast_tree.LineBreak: A LineBreak AST node.
        """
        return ast_tree.LineBreak()

    @process_prenode(NodeType.HEADING)
    def process_heading(self, node: PreNode) -> ast_tree.ASTNode:
        """Parses heading syntax and returns a Heading AST node.
        Args:
            node (PreNode): A heading PreNode.

        Returns:
            ast_tree.Heading: A Heading AST node with parsed inline children.
        """
        heading_level = len(re.findall(r"#+", node.content)[0])
        node.content = node.content.lstrip("# ").rstrip("\n")

        heading = ast_tree.Heading(level=heading_level)
        for child in self.parse_inline(node.content):
            heading.add_child(child)
        return heading

    @process_prenode(NodeType.UR_LIST_ITEM)
    def process_ur_list_item(self, node: PreNode) -> ast_tree.ASTNode:
        """Parses unordered list item into ListItem AST node.
        Args:
            node (PreNode): An unordered list item PreNode.

        Returns:
            ast_tree.ListItem: A ListItem AST node of None order with parsed inline children .
        """
        nesting_level = len(node.pre_children[0].content) - len(
            node.pre_children[0].content.lstrip()
        )
        node.pre_children[0].content = node.pre_children[0].content[nesting_level + 2 :]
        list_item = ast_tree.ListItem()
        for p_node in node.pre_children:
            if p_node.node_type == NodeType.TEXT:
                for child in self.parse_inline(p_node.content):
                    list_item.add_child(child)
            else:
                handler = self.node_funcs[p_node.node_type]
                ast_node = handler(p_node)
                list_item.add_child(ast_node)
        return list_item

    @process_prenode(NodeType.OR_LIST_ITEM)
    def process_or_list_item(self, node: PreNode) -> ast_tree.ASTNode:
        """Parses ordered list item into ListItem AST node.
        Args:
            node (PreNode): An ordered list item PreNode.

        Returns:
            ast_tree.ListItem: A ListItem AST node of numeric order with parsed inline children.
        """
        nesting_level = len(node.pre_children[0].content) - len(
            node.pre_children[0].content.lstrip()
        )
        num_len = len(re.findall(r"\s*(\d*\.\s)", node.pre_children[0].content)[0])
        match = re.match(r"^\s*(\d+)\.\s", node.pre_children[0].content)
        if match:
            order = match.group(1)
        node.pre_children[0].content = node.pre_children[0].content[
            nesting_level + num_len :
        ]
        list_item = ast_tree.ListItem(order=int(order))
        for p_node in node.pre_children:
            if p_node.node_type == NodeType.TEXT:
                for child in self.parse_inline(p_node.content):
                    list_item.add_child(child)
            else:
                handler = self.node_funcs[p_node.node_type]
                ast_node = handler(p_node)
                list_item.add_child(ast_node)
        return list_item

    @process_prenode(NodeType.TASK_LIST_ITEM)
    def process_task_list_item(self, node: PreNode) -> ast_tree.ASTNode:
        """Parses task list item into TaskListItem AST node.
        Args:
            node (PreNode): A task list item PreNode.

        Returns:
            ast_tree.TaskListItem: A TaskListItem AST node with parsed inline children.
        """
        checked_sign = re.findall(r"\[( |x|X)\]", node.pre_children[0].content)[0]
        checked_sign = not checked_sign.strip() == ""
        sign_len = len(
            re.findall(
                r"(\s*([-*+]|\d+\.)\s+\[( |x|X)\]\s)", node.pre_children[0].content
            )[0][0]
        )
        node.pre_children[0].content = node.pre_children[0].content[sign_len:]

        list_item = ast_tree.TaskListItem(checked=checked_sign)
        for p_node in node.pre_children:
            if p_node.node_type == NodeType.TEXT:
                for child in self.parse_inline(p_node.content):
                    list_item.add_child(child)
            else:
                handler = self.node_funcs[p_node.node_type]
                ast_node = handler(p_node)
                list_item.add_child(ast_node)
        return list_item

    @process_prenode(NodeType.PARAGRAPH)
    def process_paragraph(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Parses a paragraph and returns a Paragraph AST node.

        Args:
            node (PreNode): A PreNode containing paragraph text.

        Returns:
            ast_tree.Paragraph: A Paragraph AST node with parsed inline children.
        """
        paragraph_node = ast_tree.Paragraph()
        for p_node in node.pre_children:
            for inline_child in self.parse_inline(p_node.content):
                paragraph_node.add_child(inline_child)
        return paragraph_node

    @process_prenode(NodeType.BLOCKQOUTE)
    def process_blockqoute(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Parses a nested blockquote from a PreNode tree and returns a Blockquote AST node.

        Args:
            node (PreNode): The root PreNode representing a blockquote (possibly nested).

        Returns:
            ast_tree.Blockquote: A fully populated Blockquote AST node.
        """
        blockqoute_node = ast_tree.Blockquote()
        for child in node.pre_children:
            if child.node_type == NodeType.BLOCKQOUTE:
                blockqoute_node.add_child(self.process_blockqoute(child))
            else:
                child.content = child.content.lstrip(" >")
                for inline_child in self.parse_inline(child.content):
                    blockqoute_node.add_child(inline_child)
        return blockqoute_node

    @process_prenode(NodeType.CODE_BLOCK)
    def process_code_block(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Parses a code block and returns CodeBlock AST node.
        Args:
            node (PreNode): The CodeBlock pre_node.

        Returns:
            ast_tree.CodeBlock: A CodeBlock AST node.
        """
        language = re.findall(r"```(.*)\n", node.content)[0]
        first_line_len = len(re.findall(r".*\n", node.content)[0])
        code = node.content[first_line_len:]
        code_block_node = ast_tree.CodeBlock(code=code, language=language)
        return code_block_node

    @process_prenode(NodeType.TABLE)
    def process_table(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Parses table, delegates row parsing and returns Table AST node.
        Args:
            node (PreNode): The Table pre_node.

        Returns:
            ast_tree.Table: A Table AST node.
        """
        text = node.content.splitlines(keepends=True)
        pre_nodes = self.generate_prenodes(text)

        alignments = []
        header = pre_nodes[0]
        border = pre_nodes[1]
        rows = pre_nodes[2:] if len(pre_nodes) > 2 else None
        table_node = ast_tree.Table()

        border_cols = border.content.strip().split("|")
        cleaned = [s for s in border_cols if len(s) != 0]
        col_num = len(cleaned)
        for cl in cleaned:
            cl = cl.strip()
            if cl[0] == ":" and cl[-1] == ":":
                alignments.append("center")
            elif cl[-1] == ":":
                alignments.append("right")
            else:
                alignments.append("left")
        header_node = self.process_table_row(
            header.content, is_header=True, correct_len=col_num, alignments=alignments
        )
        table_node.add_child(header_node)
        for rw in rows if rows else []:
            row_node = self.process_table_row(
                rw.content, is_header=False, correct_len=col_num, alignments=alignments
            )
            table_node.add_child(row_node)
        return table_node

    @process_prenode(NodeType.TABLE_ROW)
    def process_table_row(
        self, text: str, is_header: bool, correct_len: int, alignments: list[str]
    ) -> ast_tree.ASTNode:
        """
        Parses table row and returns TableRow AST node.

        Args:
            node (PreNode): The Table Row pre_node.

        Returns:
            ast_tree.Table: A TableRow AST node.
        """
        cols = text.strip().split("|")
        cleaned = [s for s in cols if len(s) != 0]
        row_node = ast_tree.TableRow(is_header)
        if len(cleaned) != correct_len:
            raise ValueError("Number of cells in row is incorrect")
        for idx, cl in enumerate(cleaned):
            cl = cl.strip()
            cell_node = ast_tree.TableCell(alignment=alignments[idx])
            for child in self.parse_inline(cl):
                cell_node.add_child(child)
            row_node.add_child(cell_node)
        return row_node

    @process_prenode(NodeType.HORIZONTAL_RULE)
    def process_horizontal_rule(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Converts a horizontal rule PreNode into a HorizontalRule AST node.

        Args:
            node (PreNode): A PreNode of type HORIZONTAL_RULE.

        Returns:
            ast_tree.HorizontalRule: A horizontal rule node for the AST.
        """
        return ast_tree.HorizontalRule()

    @process_prenode(NodeType.LIST)
    def process_list(self, node: PreNode) -> ast_tree.ASTNode:
        """
        Converts a LIST PreNode into an AST List node.
        Determines the list type based on its first relevant child.

        Args:
            node (PreNode): A PreNode of type LIST containing nested list items.

        Returns:
            ast_tree.List: A List AST node with the appropriate type and children.
        """
        list_node = ast_tree.List(list_type="unordered")

        for child in node.pre_children:
            if child.node_type == NodeType.UR_LIST_ITEM:
                list_node.list_type = "unordered"
                break
            elif child.node_type == NodeType.OR_LIST_ITEM:
                list_node.list_type = "ordered"
                break
            elif child.node_type == NodeType.TASK_LIST_ITEM:
                list_node.list_type = "task"
                break

        for child in node.pre_children:
            handler = self.node_funcs[child.node_type]
            ast_node = handler(child)
            list_node.add_child(ast_node)

        return list_node
