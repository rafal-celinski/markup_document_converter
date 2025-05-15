from markup_document_converter.parsers.base_parser import BaseParser
from markup_document_converter.registry import register_parser
import src.markup_document_converter.ast as ast
import re
from dataclasses import dataclass, field
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


def print_node(node, indent=0):
    INDENT = "  "
    prefix = INDENT * indent

    if node.node_type == NodeType.HEADING:
        print(node.content.strip())
    elif node.node_type == NodeType.TEXT:
        print(f"{prefix}{node.content.strip()}")
    elif node.node_type == NodeType.LINE_BREAK:
        print()
    elif node.node_type == NodeType.HORIZONTAL_RULE:
        print("---")
    elif node.node_type == NodeType.BLOCKQOUTE:
        for child in node.pre_children:
            print(f"{prefix}> {child.content.strip()}")
    elif node.node_type == NodeType.UR_LIST_ITEM:
        print(f"{prefix}- {get_text_content(node)}")
    elif node.node_type == NodeType.OR_LIST_ITEM:
        print(f"{prefix}1. {get_text_content(node)}")
    elif node.node_type == NodeType.TASK_LIST_ITEM:
        content = get_text_content(node)
        print(f"{prefix}- {content.strip()}")
    elif node.node_type == NodeType.LIST:
        for child in node.pre_children:
            print_node(child, indent=indent + 1)
    else:
        for child in node.pre_children:
            print_node(child, indent=indent)


def get_text_content(node):
    """Recursively gets text content from a node."""
    if node.node_type == NodeType.TEXT:
        return node.content.strip()
    return " ".join(get_text_content(child) for child in node.pre_children)


@dataclass(order=True)
class PreNode:
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


@register_parser("md")
@register_parser("markdown")
class MarkdownParser(BaseParser):
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

        self.node_funcs: dict[NodeType, Callable[[PreNode], ast.ASTNode]] = {}

        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_node_type"):
                self.node_funcs[method._node_type] = method

    def to_AST(self, content: str) -> ast.ASTNode:
        """
        Parses markdown content and converts it to an AST.

        Args:
            content (str): Full markdown content as a string.

        Returns:
            ASTNode: Parsed AST document.
        """
        lines = content.splitlines(keepends=True)
        root = ast.Document()

        pre_nodes = self._generate_prenodes(lines)
        pre_nodes = self._group_pre_nodes(pre_nodes)

        for node in pre_nodes:
            handler = self.node_funcs[node.node_type]
            ast_node = handler(node)
            root.add_child(ast_node)

        return root

    def _group_pre_nodes(self, pre_nodes: List[PreNode]) -> List[PreNode]:
        """
        Groups consecutive TEXT nodes into PARAGRAPH nodes and retains single-line node types.

        Args:
            pre_nodes (List[PreNode]): Flat list of parsed PreNodes.

        Returns:
            List[PreNode]: Grouped PreNodes, ready for processing into AST nodes.
        """

        def group_blockqoutes(pre_nodes: list[PreNode]):
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
            def merger(
                idx: int, nesting_lvl: int, list_root: PreNode, p_nodes: list[PreNode]
            ) -> int:
                list_node = None
                list_type = None
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
                            idx = merger(idx, nesting_lvl + 1, list_node, p_nodes)
                        elif curr_nesting < nesting_lvl:
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

        if match.group("link_text") and match.group("link_url"):
            text = match.group("link_text")
            url = match.group("link_url")
            link_node = ast.Link(source=url)
            for child in self._parse_inline(text):
                link_node.add_child(child)
            return link_node

        if match.group("image_alt") and match.group("image_url"):
            alt = match.group("image_alt")
            src = match.group("image_url")
            return ast.Image(source=src, alt_text=alt)

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
        nesting_level = len(node.pre_children[0].content) - len(
            node.pre_children[0].content.lstrip()
        )
        node.pre_children[0].content = node.pre_children[0].content[nesting_level + 2 :]
        list_item = ast.ListItem()
        for p_node in node.pre_children:
            for child in self._parse_inline(p_node.content):
                list_item.add_child(child)
        return list_item

    @process_prenode(NodeType.OR_LIST_ITEM)
    def _process_or_list_item(self, node: PreNode) -> ast.ASTNode:
        """Parses ordered list item into ListItem AST node."""
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
        list_item = ast.ListItem(order=int(order))
        for p_node in node.pre_children:
            for child in self._parse_inline(p_node.content):
                list_item.add_child(child)
        return list_item

    @process_prenode(NodeType.TASK_LIST_ITEM)
    def _process_task_list_item(self, node: PreNode) -> ast.ASTNode:
        """Parses task list item into TaskListItem AST node."""
        checked_sign = re.findall(r"\[( |x|X)\]", node.pre_children[0].content)[0]
        checked_sign = not checked_sign.strip() == ""
        sign_len = len(
            re.findall(
                r"(\s*([-*+]|\d+\.)\s+\[( |x|X)\]\s)", node.pre_children[0].content
            )[0][0]
        )
        node.pre_children[0].content = node.pre_children[0].content[sign_len:]

        list_item = ast.TaskListItem(checked=checked_sign)
        for p_node in node.pre_children:
            for child in self._parse_inline(p_node.content):
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
        for p_node in node.pre_children:
            for inline_child in self._parse_inline(p_node.content):
                paragraph_node.add_child(inline_child)
        return paragraph_node

    @process_prenode(NodeType.BLOCKQOUTE)
    def _process_blockqoute(self, node: PreNode) -> ast.ASTNode:
        """
        Parses a blockqoute and returns Blockqoute AST node.
        """
        blockqoute_node = ast.Blockquote()
        for child in node.pre_children:
            if child.node_type == NodeType.BLOCKQOUTE:
                blockqoute_node.add_child(self._process_blockqoute(child))
            else:
                for inline_child in self._parse_inline(child.content):
                    blockqoute_node.add_child(inline_child)
        return blockqoute_node

    @process_prenode(NodeType.CODE_BLOCK)
    def _process_code_block(self, node: PreNode) -> ast.ASTNode:
        """
        Parses a code block and returns CodeBlock AST node.
        """
        language = re.findall(r"```(.*)\n", node.content)[0]
        first_line_len = len(re.findall(r".*\n", node.content)[0])
        code = node.content[first_line_len:]
        code_block_node = ast.CodeBlock(code=code, language=language)
        return code_block_node

    @process_prenode(NodeType.TABLE)
    def _process_table(self, node: PreNode) -> ast.ASTNode:
        """
        Parses table returns Table AST node.
        """
        text = node.content.splitlines(keepends=True)
        pre_nodes = self._generate_prenodes(text)

        alignments = []
        header = pre_nodes[0]
        border = pre_nodes[1]
        rows = pre_nodes[2:] if len(pre_nodes) > 2 else None
        table_node = ast.Table()

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
        header_node = self._process_table_row(
            header.content, is_header=True, correct_len=col_num, alignments=alignments
        )
        table_node.add_child(header_node)
        for rw in rows if rows else []:
            row_node = self._process_table_row(
                rw.content, is_header=False, correct_len=col_num, alignments=alignments
            )
            table_node.add_child(row_node)
        return table_node

    @process_prenode(NodeType.TABLE_ROW)
    def _process_table_row(
        self, text: str, is_header: bool, correct_len: int, alignments: list[str]
    ) -> ast.ASTNode:
        """
        Parses table row and returns TableRow AST node.
        """
        cols = text.strip().split("|")
        cleaned = [s for s in cols if len(s) != 0]
        row_node = ast.TableRow(is_header)
        if len(cleaned) != correct_len:
            raise ValueError("Number of cells in row is incorrect")
        for idx, cl in enumerate(cleaned):
            cl = cl.strip()
            cell_node = ast.TableCell(alignment=alignments[idx])
            for child in self._parse_inline(cl):
                cell_node.add_child(child)
            row_node.add_child(cell_node)
        return row_node

    @process_prenode(NodeType.HORIZONTAL_RULE)
    def _process_horizontal_rule(self, node: PreNode) -> ast.ASTNode:
        return ast.HorizontalRule()

    @process_prenode(NodeType.LIST)
    def _process_list(self, node: PreNode) -> ast.ASTNode:
        list_node = ast.List(list_type="unordered")

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
