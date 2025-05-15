from src.markup_document_converter.parsers.base_parser import BaseParser
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
            # NodeType.TASK_LIST_ITEM: r"^\s*([-*+]|\d+\.)\s+\[( |x|X)\]\s+.*\n$",
            # NodeType.UR_LIST_ITEM: r"^\s*[-*+]\s.*\n$",
            # NodeType.OR_LIST_ITEM: r"^\s*\d+\.\s+.*\n$",
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

        for nd in pre_nodes:
            print(nd)

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
            single_types = [NodeType.HEADING, NodeType.LINE_BREAK, NodeType.CODE_BLOCK]
            grouped = []
            grouping_node = None

            for node in pre_nodes:
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

            if grouping_node:
                grouped.append(grouping_node)

            return grouped

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

        post_change_incorrect_table_rows = group_table_rows(pre_nodes)
        post_blockqoutes = group_blockqoutes(post_change_incorrect_table_rows)
        post_code_blocks = group_code_blocks(post_blockqoutes)
        post_lists = group_lists(post_code_blocks)

        return post_lists

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
                    if nesting_lvl != 0:
                        return idx
                    else:
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

    # @process_prenode(NodeType.UR_LIST_ITEM)
    # def _process_ur_list_item(self, node: PreNode) -> ast.ASTNode:
    #     """Parses unordered list item into ListItem AST node."""
    #     nesting_level = len(node.content) - len(node.content.lstrip())
    #     node.content = node.content[nesting_level + 2 :]
    #     list_item = ast.ListItem(order="unordered", nesting=nesting_level)
    #     for child in self._parse_inline(node.content):
    #         list_item.add_child(child)
    #     return list_item

    # @process_prenode(NodeType.OR_LIST_ITEM)
    # def _process_or_list_item(self, node: PreNode) -> ast.ASTNode:
    #     """Parses ordered list item into ListItem AST node."""
    #     nesting_level = len(node.content) - len(node.content.lstrip())
    #     num_len = len(re.findall(r"\s*(\d*\.\s)", node.content)[0])
    #     node.content = node.content[nesting_level + num_len :]
    #     list_item = ast.ListItem(order="ordered", nesting=nesting_level)
    #     for child in self._parse_inline(node.content):
    #         list_item.add_child(child)
    #     return list_item

    # @process_prenode(NodeType.TASK_LIST_ITEM)
    # def _process_task_list_item(self, node: PreNode) -> ast.ASTNode:
    #     """Parses task list item into TaskListItem AST node."""
    #     nesting_level = len(node.content) - len(node.content.lstrip())
    #     checked_sign = re.findall(r"\[( |x|X)\]", node.content)[0]
    #     checked_sign = not checked_sign.strip() == ""
    #     sign_len = len(
    #         re.findall(r"(\s*([-*+]|\d+\.)\s+\[( |x|X)\]\s)", node.content)[0][0]
    #     )
    #     node.content = node.content[sign_len:]

    #     list_item = ast.TaskListItem(nesting=nesting_level, checked=checked_sign)
    #     for child in self._parse_inline(node.content):
    #         list_item.add_child(child)
    #     return list_item

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
