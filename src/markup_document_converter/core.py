from markup_document_converter.registry import get_parser, get_converter


def convert_document(content: str, source_format: str, target_format: str) -> str:
    """
    Convert the given document content from the source format into the target format
    using a universal AST.

    Args:
        content (str): Source document content as a string.
        source_format (str): Key identifying the input parser format
                             (e.g., 'markdown', 'rst').
        target_format (str): Key identifying the output converter format
                             (e.g., 'typst', 'latex').

    Returns:
        str: The fully rendered document in the target format.

    Raises:
        ValueError: If no parser or converter is found for the given format keys.
        Exception: Propagates any parsing or conversion errors.
    """

    parser = get_parser(source_format)

    ast_root = parser.to_AST(content)

    converter = get_converter(target_format)
    return converter.convert_document(ast_root)
