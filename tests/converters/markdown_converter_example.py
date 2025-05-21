from src.markup_document_converter.parsers.markdown_parser import (
    MarkdownParser,
)
from src.markup_document_converter.cli import get_content


def print_ast(node, indent=0):
    prefix = "  " * indent
    print(f"{prefix}- {node.node_type}", end="")

    if node.attributes:
        attr_str = ", ".join(f"{k}={repr(v)}" for k, v in node.attributes.items())
        print(f" ({attr_str})")
    else:
        print()

    for child in node.children:
        print_ast(child, indent + 1)


def main():
    parser = MarkdownParser()
    content = get_content("./tests/converters/basic.md")
    root = parser.to_AST(content)
    print_ast(root)
