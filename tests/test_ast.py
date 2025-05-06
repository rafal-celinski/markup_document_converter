from markup_document_converter.ast import (
    ASTNode,
    Document,
    Heading,
    Bold,
    Italic,
    Strike,
    Text,
    Paragraph,
    LineBreak,
    Blockquote,
    List,
    ListItem,
    CodeBlock,
    InlineCode,
    Image,
    Link,
    HorizontalRule,
    Table,
    TableRow,
    TableCell,
    TaskListItem,
)


class TestASTNode:
    def test_init(self):
        node = ASTNode("test_type")
        assert node.node_type == "test_type"
        assert node.children == []
        assert node.attributes == {}

    def test_init_with_children(self):
        child = ASTNode("child")
        node = ASTNode("parent", [child])
        assert node.children == [child]

    def test_init_with_attributes(self):
        node = ASTNode("test", attributes={"key": "value"})
        assert node.attributes == {"key": "value"}

    def test_add_child(self):
        node = ASTNode("parent")
        child = ASTNode("child")
        node.add_child(child)
        assert node.children == [child]

    def test_set_attribute(self):
        node = ASTNode("test")
        node.set_attribute("key", "value")
        assert node.attributes == {"key": "value"}


class TestDocument:
    def test_init(self):
        document = Document()
        assert document.node_type == "document"
        assert document.children == []
        assert document.attributes == {}

    def test_init_with_children(self):
        child = Text("Text")
        bold = Document([child])
        assert bold.children == [child]


class TestHeading:
    def test_init(self):
        heading = Heading(2)
        assert heading.node_type == "heading"
        assert heading.level == 2
        assert heading.children == []

    def test_init_with_children(self):
        child = Text("Title")
        heading = Heading(1, [child])
        assert heading.level == 1
        assert heading.children == [child]

    def test_level_property(self):
        heading = Heading(2)
        assert heading.level == 2
        heading.level = 3
        assert heading.level == 3
        assert heading.attributes["level"] == 3


class TestBold:
    def test_init(self):
        bold = Bold()
        assert bold.node_type == "bold"
        assert bold.children == []
        assert bold.attributes == {}

    def test_init_with_children(self):
        child = Text("Bold text")
        bold = Bold([child])
        assert bold.children == [child]


class TestItalic:
    def test_init(self):
        italic = Italic()
        assert italic.node_type == "italic"
        assert italic.children == []
        assert italic.attributes == {}

    def test_init_with_children(self):
        child = Text("Italic text")
        italic = Italic([child])
        assert italic.children == [child]


class TestStrike:
    def test_init(self):
        strike = Strike()
        assert strike.node_type == "strike"
        assert strike.children == []
        assert strike.attributes == {}

    def test_init_with_children(self):
        child = Text("Strike text")
        strike = Strike([child])
        assert strike.children == [child]


class TestText:
    def test_init(self):
        text = Text("Hello world")
        assert text.node_type == "text"
        assert text.text == "Hello world"
        assert text.attributes["text"] == "Hello world"

    def test_text_property(self):
        text = Text("Hello")
        assert text.text == "Hello"
        text.text = "World"
        assert text.text == "World"
        assert text.attributes["text"] == "World"

    def test_empty_text(self):
        text = Text("")
        assert text.text == ""
        assert text.attributes["text"] == ""


class TestParagraph:
    def test_init(self):
        para = Paragraph()
        assert para.node_type == "paragraph"
        assert para.children == []
        assert para.attributes == {}

    def test_init_with_children(self):
        text = Text("Hello")
        bold = Bold([Text("world")])
        para = Paragraph([text, bold])
        assert para.children == [text, bold]


class TestLineBreak:
    def test_init(self):
        br = LineBreak()
        assert br.node_type == "line_break"
        assert br.children == []
        assert br.attributes == {}


class TestBlockquote:
    def test_init(self):
        quote = Blockquote()
        assert quote.node_type == "blockquote"
        assert quote.children == []
        assert quote.attributes == {}

    def test_init_with_children(self):
        para = Paragraph([Text("Quoted text")])
        quote = Blockquote([para])
        assert quote.children == [para]


class TestList:
    def test_init(self):
        list_node = List("ordered")
        assert list_node.node_type == "list"
        assert list_node.list_type == "ordered"
        assert list_node.children == []

    def test_list_type_property(self):
        list_node = List("ordered")
        assert list_node.list_type == "ordered"
        list_node.list_type = "unordered"
        assert list_node.list_type == "unordered"
        assert list_node.attributes["list_type"] == "unordered"

    def test_init_with_children(self):
        item1 = ListItem(1, [Text("First")])
        item2 = ListItem(2, [Text("Second")])
        list_node = List("ordered", [item1, item2])
        assert list_node.children == [item1, item2]


class TestListItem:
    def test_init(self):
        item = ListItem(1)
        assert item.node_type == "list_item"
        assert item.order == 1
        assert item.children == []

    def test_order_property(self):
        item = ListItem(1)
        assert item.order == 1
        item.order = 2
        assert item.order == 2
        assert item.attributes["order"] == 2

    def test_init_with_children(self):
        text = Text("Item text")
        item = ListItem(1, [text])
        assert item.children == [text]


class TestCodeBlock:
    def test_init(self):
        code = CodeBlock("print('hello')", "python")
        assert code.node_type == "code_block"
        assert code.code == "print('hello')"
        assert code.language == "python"
        assert code.attributes["code"] == "print('hello')"
        assert code.attributes["language"] == "python"

    def test_code_property(self):
        code = CodeBlock("print('hello')", "python")
        assert code.code == "print('hello')"
        code.code = "console.log('hello')"
        assert code.code == "console.log('hello')"
        assert code.attributes["code"] == "console.log('hello')"

    def test_language_property(self):
        code = CodeBlock("print('hello')", "python")
        assert code.language == "python"
        code.language = "javascript"
        assert code.language == "javascript"
        assert code.attributes["language"] == "javascript"

    def test_empty_values(self):
        code = CodeBlock("", "")
        assert code.code == ""
        assert code.language == ""


class TestInlineCode:
    def test_init(self):
        code = InlineCode("var x = 10", "javascript")
        assert code.node_type == "inline_code"
        assert code.code == "var x = 10"
        assert code.attributes["code"] == "var x = 10"
        assert code.language == "javascript"
        assert code.attributes["language"] == "javascript"

    def test_code_property(self):
        code = InlineCode("var x = 10", "javascript")
        assert code.code == "var x = 10"
        code.code = "let y = 20"
        assert code.code == "let y = 20"
        assert code.attributes["code"] == "let y = 20"

    def test_language_property(self):
        code = InlineCode("print('hello')", "python")
        assert code.language == "python"
        code.language = "javascript"
        assert code.language == "javascript"
        assert code.attributes["language"] == "javascript"

    def test_empty_code(self):
        code = InlineCode("", "")
        assert code.code == ""
        assert code.language == ""


class TestImage:
    def test_init(self):
        img = Image("image.jpg", "Alt text")
        assert img.node_type == "image"
        assert img.source == "image.jpg"
        assert img.alt_text == "Alt text"
        assert img.attributes["source"] == "image.jpg"
        assert img.attributes["alt_text"] == "Alt text"

    def test_source_property(self):
        img = Image("image.jpg", "Alt text")
        assert img.source == "image.jpg"
        img.source = "new-image.png"
        assert img.source == "new-image.png"
        assert img.attributes["source"] == "new-image.png"

    def test_alt_text_property(self):
        img = Image("image.jpg", "Alt text")
        assert img.alt_text == "Alt text"
        img.alt_text = "New alt text"
        assert img.alt_text == "New alt text"
        assert img.attributes["alt_text"] == "New alt text"

    def test_empty_values(self):
        img = Image("", "")
        assert img.source == ""
        assert img.alt_text == ""


class TestLink:
    def test_init(self):
        link = Link("https://example.com")
        assert link.node_type == "link"
        assert link.source == "https://example.com"
        assert link.attributes["source"] == "https://example.com"

    def test_source_property(self):
        link = Link("https://example.com")
        assert link.source == "https://example.com"
        link.source = "https://new-example.com"
        assert link.source == "https://new-example.com"
        assert link.attributes["source"] == "https://new-example.com"

    def test_empty_values(self):
        link = Link("", "")
        assert link.source == ""

    def test_init_with_children(self):
        child = Text("Quoted text")
        link = Link("https://example.com", children=[child])
        assert link.children == [child]


class TestHorizontalRule:
    def test_init(self):
        hr = HorizontalRule()
        assert hr.node_type == "horizontal_rule"
        assert hr.children == []
        assert hr.attributes == {}


class TestTable:
    def test_init(self):
        table = Table()
        assert table.node_type == "table"
        assert table.children == []
        assert table.attributes == {}

    def test_init_with_children(self):
        header = TableRow(True, [TableCell(None, [Text("Header")])])
        row = TableRow(False, [TableCell(None, [Text("Cell")])])
        table = Table([header, row])
        assert table.children == [header, row]


class TestTableRow:
    def test_init(self):
        row = TableRow()
        assert row.node_type == "table_row"
        assert row.is_header is False
        assert row.children == []

    def test_init_with_header(self):
        row = TableRow(True)
        assert row.is_header is True
        assert row.attributes["is_header"] is True

    def test_is_header_property(self):
        row = TableRow(False)
        assert row.is_header is False
        row.is_header = True
        assert row.is_header is True
        assert row.attributes["is_header"] is True

    def test_init_with_children(self):
        cell1 = TableCell(None, [Text("Cell 1")])
        cell2 = TableCell(None, [Text("Cell 2")])
        row = TableRow(False, [cell1, cell2])
        assert row.children == [cell1, cell2]


class TestTableCell:
    def test_init(self):
        cell = TableCell()
        assert cell.node_type == "table_cell"
        assert cell.alignment == "left"
        assert cell.children == []

    def test_init_with_alignment(self):
        cell = TableCell("center")
        assert cell.alignment == "center"
        assert cell.attributes["alignment"] == "center"

    def test_alignment_property(self):
        cell = TableCell("left")
        assert cell.alignment == "left"
        cell.alignment = "right"
        assert cell.alignment == "right"
        assert cell.attributes["alignment"] == "right"

    def test_init_with_children(self):
        text = Text("Cell content")
        cell = TableCell(None, [text])
        assert cell.children == [text]


class TestTaskListItem:
    def test_init(self):
        item = TaskListItem()
        assert item.node_type == "task_list_item"
        assert item.checked is False
        assert item.children == []

    def test_init_with_checked(self):
        item = TaskListItem(True)
        assert item.checked is True
        assert item.attributes["checked"] is True

    def test_checked_property(self):
        item = TaskListItem(False)
        assert item.checked is False
        item.checked = True
        assert item.checked is True
        assert item.attributes["checked"] is True

    def test_init_with_children(self):
        text = Text("Task description")
        item = TaskListItem(False, [text])
        assert item.children == [text]
