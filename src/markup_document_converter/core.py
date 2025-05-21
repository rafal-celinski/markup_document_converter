import os
from markup_document_converter.registry import get_parser, get_converter


def convert_document(input_path: str, target_format: str) -> str:
    """
    Read a source file, parse its content into the universal AST, and render it via the
    specified converter.

    Args:
        input_path (str): Path to the input file (e.g. 'README.md').
        target_format (str): Key for the desired converter (e.g. 'typst', 'latex').

    Returns:
        str: The fully rendered document in the target format.

    Raises:
        FileNotFoundError: If `input_path` does not exist or is not readable.
        ValueError: If no parser or converter is found for the given names.
        Exception: Propagates any parsing or conversion errors.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    content = get_content(input_path)

    _, ext = os.path.splitext(input_path)
    parser_name = ext.lstrip(".").lower()
    parser = get_parser(parser_name)

    ast_root = parser.to_AST(content)

    converter = get_converter(target_format)
    return converter.convert_document(ast_root)


def get_content(input_path: str) -> str:
    with open(input_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    if not content.endswith("\n"):
        content += "\n"
    return content
