from src.markup_document_converter.converters.base_converter import BaseConverter
import src.markup_document_converter.ast as ast
import re


class MarkdownConverter(BaseConverter):
    def to_AST(self, input_file: str) -> ast.ASTNode:
        """
        Parses a markup file and converts it to an AST.

        Args:
            input_file (str): Path to the markup file.

        Returns:
            ASTNode: Parsed AST tree.
        """
        tags_values = {
            "#": "\n",
            "-": "\n",
        }
        with open(input_file, "r") as fp:
            text = fp.read()

        if text[-1] != "\n":
            text += "\n"
        root = ast.Document()

        idx = 0
        while idx < len(text):
            start_char = text[idx]
            if start_char in tags_values.keys():
                end_char = tags_values[start_char]
            else:
                end_char = "\n"
            end_idx = self._find_next(end_char, text, idx)
            block = text[idx : end_idx + 1]
            root.add_child(self._parse_block(block, start_char))
            idx = end_idx + 1
        return root

    def _find_next(self, char, text, idx):
        j = idx
        while True:
            if text[j] == char:
                return j
            j += 1

    def _parse_block(self, block, start_char):
        if start_char == "#":
            heading_level = len(re.findall(r"#+", block)[0])
            return ast.Heading(
                level=heading_level, children=self._parse_heading(block[heading_level:])
            )
        else:
            return ast.Text(block)

    def _parse_heading(self, heading):
        return [ast.Text(heading)]

    def to_file(self, ast_root):
        return "Work in progress"
