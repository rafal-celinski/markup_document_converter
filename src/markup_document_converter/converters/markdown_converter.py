from src.markup_document_converter.converters.base_converter import BaseConverter
import src.markup_document_converter.ast as ast
import re
from dataclasses import dataclass


@dataclass(order=True)
class PreNode:
    start_idx: int
    content: str
    pattern_name: str


class MarkdownConverter(BaseConverter):
    def to_AST(self, input_file: str) -> ast.ASTNode:
        """
        Parses a markup file and converts it to an AST.

        Args:
            input_file (str): Path to the markup file.

        Returns:
            ASTNode: Parsed AST tree.
        """

        patterns = {
            "heading": r"^(#+)\s.*\n",
            "list": r"^(\s*)-\s.*\n",
        }

        with open(input_file, "r") as fp:
            text = fp.read()

        # Add \n at the end of the file so that algorithm works everytime
        if text[-1] != "\n":
            text += "\n"
        root = ast.Document()

        # Generating pre-nodes that will be converted to AST nodes
        pre_nodes = []
        for name in patterns:
            pattern = re.compile(patterns[name], re.MULTILINE)
            for match in pattern.finditer(text):
                print(match.group())
                pre_nodes.append(PreNode(match.start(), match.group(), name))

        pre_nodes.sort()

        print(pre_nodes)

        # Creating pre-nodes for unmatched text
        filled_nodes = []
        current_pos = 0
        for node in pre_nodes:
            if current_pos < node.start_idx:
                unmatched_text = text[current_pos : node.start_idx]
                filled_nodes.append(PreNode(current_pos, unmatched_text, "text"))
            filled_nodes.append(node)
            current_pos = node.start_idx + len(node.content)

        print(filled_nodes)

        # Don't forget the end
        if current_pos < len(text):
            tail_text = text[current_pos:]
            filled_nodes.append(PreNode(current_pos, tail_text, "text"))

        for node in filled_nodes:
            if node.pattern_name == "heading":
                heading_level = len(re.findall(r"#+", node.content)[0])
                root.add_child(
                    ast.Heading(
                        level=heading_level,
                        children=[ast.Text(node.content[heading_level:])],
                    )
                )
            elif node.pattern_name == "list":
                root.add_child(
                    ast.ListItem(order="unordered", children=[ast.Text(node.content)])
                )
            elif node.pattern_name == "text":
                root.add_child(ast.Text(node.content))

        return root

    def to_file(self, ast_root):
        return "In progress"
