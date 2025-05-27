import pytest
from markup_document_converter.parsers.markdown_parser import (
    MarkdownParser,
    print_node,
    PreNode,
    NodeType,
)
import markup_document_converter.ast_tree as ast_tree
import io
import contextlib


@pytest.fixture
def parser():
    return MarkdownParser()


def extract_text(node):
    """Recursively collect raw text from AST nodes."""
    if isinstance(node, ast_tree.Text):
        return node.text
    text = ""
    for child in getattr(node, "children", []):
        text += extract_text(child)
    return text


def test_heading_level_1(parser):
    doc = parser.to_AST("# Title\n")
    assert isinstance(doc, ast_tree.Document)
    assert len(doc.children) == 1
    h = doc.children[0]
    assert isinstance(h, ast_tree.Heading)
    assert h.level == 1
    assert extract_text(h) == "Title"


def test_paragraph_and_line_breaks(parser):
    md = "Line1\nLine2\n\nNext paragraph\n"
    doc = parser.to_AST(md)
    # first paragraph
    p1 = doc.children[0]
    assert isinstance(p1, ast_tree.Paragraph)
    assert extract_text(p1) == "Line1\nLine2\n"
    lb = doc.children[1]
    assert isinstance(lb, ast_tree.LineBreak)
    # second paragraph
    p2 = doc.children[2]
    assert isinstance(p2, ast_tree.Paragraph)
    assert extract_text(p2) == "Next paragraph\n"


def test_unordered_list(parser):
    md = "- item1\n- item2\n"
    doc = parser.to_AST(md)
    lst = doc.children[0]
    assert isinstance(lst, ast_tree.List)
    items = lst.children
    assert len(items) == 2
    assert extract_text(items[0]) == "item1\n"
    assert extract_text(items[1]) == "item2\n"


def test_ordered_list(parser):
    md = "1. first\n2. second\n"
    doc = parser.to_AST(md)
    lst = doc.children[0]
    assert isinstance(lst, ast_tree.List)
    items = lst.children
    assert len(items) == 2
    assert extract_text(items[0]) == "first\n"
    assert extract_text(items[1]) == "second\n"


def test_task_list(parser):
    md = "- [ ] unchecked\n- [x] checked\n"
    doc = parser.to_AST(md)
    lst = doc.children[0]
    assert isinstance(lst, ast_tree.List)
    items = lst.children
    assert isinstance(items[0], ast_tree.TaskListItem)
    assert items[0].checked is False
    assert extract_text(items[0]) == "unchecked\n"
    assert isinstance(items[1], ast_tree.TaskListItem)
    assert items[1].checked is True
    assert extract_text(items[1]) == "checked\n"


def test_horizontal_rule(parser):
    md = "---\n"
    doc = parser.to_AST(md)
    hr = doc.children[0]
    assert isinstance(hr, ast_tree.HorizontalRule)


def test_code_block(parser):
    md = "```py\nprint('hello')\n```\n"
    doc = parser.to_AST(md)
    cb = doc.children[0]
    assert isinstance(cb, ast_tree.CodeBlock)
    assert cb.language == "py"
    assert "print('hello')" in cb.code


def test_inline_formatting(parser):
    md = "***bolditalic*** **bold** *italic* ~~strike~~ `code`\n"
    doc = parser.to_AST(md)
    p = doc.children[0]
    # should contain Bold, Italic, Strike, InlineCode nodes
    assert any(isinstance(n, ast_tree.Bold) for n in p.children)
    assert any(isinstance(n, ast_tree.Italic) for n in p.children)
    assert any(isinstance(n, ast_tree.Strike) for n in p.children)
    assert any(isinstance(n, ast_tree.InlineCode) for n in p.children)


def test_link_and_image(parser):
    md = "Here [link](http://x) and ![alt](img.png)\n"
    doc = parser.to_AST(md)
    p = doc.children[0]
    link = next(n for n in p.children if isinstance(n, ast_tree.Link))
    assert link.source == "http://x"
    assert extract_text(link) == "link"
    img = next(n for n in p.children if isinstance(n, ast_tree.Image))
    assert img.source == "img.png"
    assert img.alt_text == "alt"


def test_blockquote(parser):
    md = "> Quote line\n"
    doc = parser.to_AST(md)
    bq = doc.children[0]
    assert isinstance(bq, ast_tree.Blockquote)
    # lines concatenated
    assert extract_text(bq) == "Quote line\n"


def test_nested_blockqoutes(parser):
    md = "> Quote line\n>> Nested quote\n"
    doc = parser.to_AST(md)
    bq = doc.children[0]
    assert isinstance(bq, ast_tree.Blockquote)
    assert len(bq.children) == 2
    assert isinstance(bq.children[0], ast_tree.Text)
    assert isinstance(bq.children[1], ast_tree.Blockquote)
    assert extract_text(bq.children[0]) == "Quote line\n"
    assert extract_text(bq.children[1]) == "Nested quote\n"


def test_table(parser):
    md = "|H1|H2|\n|--|--|\n|a|b|\n"
    doc = parser.to_AST(md)
    table = doc.children[0]
    assert isinstance(table, ast_tree.Table)
    header = table.children[0]
    assert isinstance(header, ast_tree.TableRow)
    cells = header.children
    assert len(cells) == 2
    assert extract_text(cells[0]) == "H1"
    assert extract_text(cells[1]) == "H2"
    row = table.children[1]
    cells = row.children
    assert extract_text(cells[0]) == "a"
    assert extract_text(cells[1]) == "b"


def test_empty_content(parser):
    # edge case: empty string produces empty Document
    doc = parser.to_AST("")
    assert isinstance(doc, ast_tree.Document)
    assert doc.children == []


def test_print_node_basic():
    # TEXT node
    node_text = PreNode(node_type=NodeType.TEXT, content="hello\n")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_node(node_text)
    assert buf.getvalue() == "hello\n"

    # LINE_BREAK node
    node_lb = PreNode(node_type=NodeType.LINE_BREAK)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_node(node_lb)
    assert buf.getvalue() == "\n"

    # HORIZONTAL_RULE node
    node_hr = PreNode(node_type=NodeType.HORIZONTAL_RULE)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_node(node_hr)
    assert buf.getvalue() == "---\n"
