import markup_document_converter.ast as ast
from markup_document_converter.converters.typst_converter import TypstConverter
import pytest  # type: ignore


@pytest.fixture(scope="class")
def typst_converter(request):
    request.cls.typst_converter = TypstConverter()


@pytest.mark.usefixtures("typst_converter")
class TestTypstConverter:
    def test_convert_default(self):
        pass

    def test_convert_document(self):
        document = ast.Document(
            children=[
                ast.Heading(
                    level=1,
                    children=[ast.Text("Heading 1")],
                ),
                ast.Text("Text "),
                ast.Bold(
                    children=[
                        ast.Text("Bold text"),
                    ]
                ),
            ]
        )

        result = document.convert(self.typst_converter)

        assert result == "\n" "= Heading 1\n" "Text *Bold text*\n"

    def test_empty_document(self):
        document = ast.Document([])
        result = document.convert(self.typst_converter)
        assert result == "\n"

    @pytest.mark.parametrize(
        "level,expected",
        [
            (1, "\n= Heading\n"),
            (2, "\n== Heading\n"),
            (3, "\n=== Heading\n"),
            (4, "\n==== Heading\n"),
            (5, "\n===== Heading\n"),
            (6, "\n====== Heading\n"),
        ],
    )
    def test_convert_heading(self, level, expected):
        heading = ast.Heading(
            level=level,
            children=[ast.Text("Heading")],
        )

        result = heading.convert(self.typst_converter)

        assert result == expected

    def test_empty_heading(self):
        heading = ast.Heading(level=1)

        result = heading.convert(self.typst_converter)

        assert result == "\n= \n"

    def test_convert_bold(self):
        bold = ast.Bold(children=[ast.Text("Bold text")])

        result = bold.convert(self.typst_converter)

        assert result == "*Bold text*"

    def test_bold_empty(self):
        bold = ast.Bold([])
        result = bold.convert(self.typst_converter)
        assert result == "**"

    def test_convert_italic(self):
        italic = ast.Italic(children=[ast.Text("Italic text")])

        result = italic.convert(self.typst_converter)

        assert result == "_Italic text_"

    def test_empty_italic(self):
        italic = ast.Italic()

        result = italic.convert(self.typst_converter)

        assert result == "__"

    def test_convert_strike(self):
        strike = ast.Strike(children=[ast.Text("Strike text")])

        result = strike.convert(self.typst_converter)

        assert result == "#strike[Strike text]"

    def test_empty_strike(self):
        strike = ast.Strike()

        result = strike.convert(self.typst_converter)

        assert result == "#strike[]"

    def test_convert_text(self):
        text = ast.Text("Text")

        result = text.convert(self.typst_converter)

        assert result == "Text"

    def test_convert_paragraph(self):
        paragraph = ast.Paragraph(children=[ast.Text("Paragraph")])

        result = paragraph.convert(self.typst_converter)

        assert result == "\nParagraph\n"

    def test_empty_paragraph(self):
        paragraph = ast.Paragraph()

        result = paragraph.convert(self.typst_converter)

        assert result == "\n\n"

    def test_convert_line_break(self):
        line_break = ast.LineBreak()

        result = line_break.convert(self.typst_converter)

        assert result == "\\ "

    def test_convert_blockquote(self):
        blockquote = ast.Blockquote(children=[ast.Text("Blockquote")])

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Blockquote]"

    def test_empty_blockquote(self):
        blockquote = ast.Blockquote()

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[]"

    def test_nested_blockquote(self):
        blockquote = ast.Blockquote(
            children=[
                ast.Text("Blockquote "),
                ast.Blockquote(children=[ast.Text("Nested Blockquote")]),
            ]
        )

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Blockquote #quote[Nested Blockquote]]"

    def test_convert_ordered_list(self):
        ordered_list = ast.List(
            list_type="ordered",
            children=[
                ast.ListItem(
                    order=1,
                    children=[ast.Text("Item 1")],
                ),
                ast.ListItem(
                    order=2,
                    children=[ast.Text("Item 2")],
                ),
                ast.ListItem(
                    order=3,
                    children=[ast.Text("Item 3")],
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n1. Item 1\n" + "2. Item 2\n" + "3. Item 3\n"

    def test_convert_autoordered_list(self):
        ordered_list = ast.List(
            list_type="ordered",
            children=[
                ast.ListItem(children=[ast.Text("Item 1")]),
                ast.ListItem(children=[ast.Text("Item 2")]),
                ast.ListItem(children=[ast.Text("Item 3")]),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n+ Item 1\n" + "+ Item 2\n" + "+ Item 3\n"

    def test_convert_unordered_list(self):
        unordered_list = ast.List(
            list_type="unordered",
            children=[
                ast.ListItem(children=[ast.Text("Item 1")]),
                ast.ListItem(children=[ast.Text("Item 2")]),
                ast.ListItem(children=[ast.Text("Item 3")]),
            ],
        )

        result = unordered_list.convert(self.typst_converter)

        assert result == "\n- Item 1\n" + "- Item 2\n" + "- Item 3\n"

    def test_convert_nested_list(self):
        nested_list = ast.List(
            list_type="unordered",
            children=[
                ast.ListItem(children=[ast.Text("Item 1")]),
                ast.ListItem(children=[ast.Text("Item 2")]),
                ast.ListItem(children=[ast.Text("Item 3")]),
                ast.ListItem(
                    children=[
                        ast.Text("Item 4"),
                        ast.List(
                            list_type="unordered",
                            children=[
                                ast.ListItem(children=[ast.Text("Item 4a")]),
                                ast.ListItem(children=[ast.Text("Item 4b")]),
                                ast.ListItem(children=[ast.Text("Item 4c")]),
                            ],
                        ),
                        ast.Text("some additional text"),
                    ]
                ),
                ast.ListItem(children=[ast.Text("Item 5")]),
            ],
        )

        result = nested_list.convert(self.typst_converter)

        assert (
            result
            == "\n- Item 1\n"
            + "- Item 2\n"
            + "- Item 3\n"
            + "- Item 4\n"
            + "\t- Item 4a\n"
            + "\t- Item 4b\n"
            + "\t- Item 4c\n"
            + "\tsome additional text\n"
            + "- Item 5\n"
        )

    def test_empty_list(self):
        ordered_list = ast.List("ordered")

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n"

    def test_convert_list_item_single_text(self):
        list_item = ast.ListItem(children=[ast.Text("Item")])

        result = list_item.convert(self.typst_converter)

        assert result == "Item\n"

    def test_convert_list_item_multiple_text(self):
        list_item = ast.ListItem(
            children=[ast.Bold(children=[ast.Text("Bold")]), ast.Text(" Item")]
        )

        result = list_item.convert(self.typst_converter)

        assert result == "*Bold* Item\n"

    def test_convert_list_item_indent_list(self):
        list_item = ast.ListItem(
            children=[
                ast.Text("Item"),
                ast.List(
                    list_type="unordered",
                    children=[ast.ListItem(children=[ast.Text("Indent item")])],
                ),
            ]
        )

        result = list_item.convert(self.typst_converter)

        assert result == "Item\n" + "- Indent item\n"

    def test_convert_empty_list_item(self):
        list_item = ast.ListItem()

        result = list_item.convert(self.typst_converter)

        assert result == "\n"

    def test_convert_code_block(self):
        code_block = ast.CodeBlock(language="python", code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```python\nprint('Hello World!')\n```"

    def test_code_block_without_language(self):
        code_block = ast.CodeBlock(code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```\nprint('Hello World!')\n```"

    def test_convert_inline_code(self):
        inline_code = ast.InlineCode(language="python", code="print('Hello World!')")

        result = inline_code.convert(self.typst_converter)

        assert result == "```python print('Hello World!')```"

    def test_convert_inline_code_without_language(self):
        inline_code = ast.InlineCode(code="print('Hello World!')")

        result = inline_code.convert(self.typst_converter)

        assert result == "```print('Hello World!')```"

    def test_convert_image(self):
        image = ast.Image(source="image.png", alt_text="example image")

        result = image.convert(self.typst_converter)

        assert result == '#image("image.png", alt: "example image")'

    def test_convert_image_without_alt(self):
        image = ast.Image(source="image.png")

        result = image.convert(self.typst_converter)

        assert result == '#image("image.png")'

    def test_convert_link_with_text(self):
        link = ast.Link(
            source="example.com",
            children=[ast.Text("Link text")],
        )

        result = link.convert(self.typst_converter)

        assert result == '#link("example.com")[Link text]'

    def test_convert_link_without_text(self):
        link = ast.Link(source="example.com")

        result = link.convert(self.typst_converter)

        assert result == '#link("example.com")'

    def test_convert_horizontal_rule(self):
        hr = ast.HorizontalRule()

        result = hr.convert(self.typst_converter)

        assert result == "#line(length: 100%)"

    def test_convert_table(self):
        table = ast.Table(
            children=[
                ast.TableRow(
                    is_header=True,
                    children=[
                        ast.TableCell(children=[ast.Text("cell_00")]),
                        ast.TableCell(children=[ast.Text("cell_01")]),
                        ast.TableCell(children=[ast.Text("cell_02")]),
                    ],
                ),
                ast.TableRow(
                    is_header=False,
                    children=[
                        ast.TableCell(children=[ast.Text("cell_10")]),
                        ast.TableCell(children=[ast.Text("cell_11")]),
                        ast.TableCell(children=[ast.Text("cell_12")]),
                    ],
                ),
                ast.TableRow(
                    is_header=False,
                    children=[
                        ast.TableCell(children=[ast.Text("cell_20")]),
                        ast.TableCell(children=[ast.Text("cell_21")]),
                    ],
                ),
            ]
        )

        result = table.convert(self.typst_converter)

        assert (
            result
            == "\n#table(\n"
            + "\tcolumns: 3,\n"
            + "\t[cell_00], [cell_01], [cell_02], \n"
            + "\t[cell_10], [cell_11], [cell_12], \n"
            + "\t[cell_20], [cell_21], [], \n"
            + ")\n"
        )

    def test_convert_empty_table(self):
        table = ast.Table()

        result = table.convert(self.typst_converter)

        assert result == "\n#table(\n" + "\tcolumns: 0,\n" + ")\n"

    def test_convert_table_empty_row(self):
        table = ast.Table(
            children=[
                ast.TableRow(
                    is_header=True,
                    children=[
                        ast.TableCell(children=[ast.Text("cell_00")]),
                        ast.TableCell(children=[ast.Text("cell_01")]),
                        ast.TableCell(children=[ast.Text("cell_02")]),
                    ],
                ),
                ast.TableRow(is_header=False),
                ast.TableRow(
                    is_header=False,
                    children=[
                        ast.TableCell(children=[ast.Text("cell_20")]),
                        ast.TableCell(children=[ast.Text("cell_21")]),
                    ],
                ),
            ]
        )

        result = table.convert(self.typst_converter)

        assert (
            result
            == "\n#table(\n"
            + "\tcolumns: 3,\n"
            + "\t[cell_00], [cell_01], [cell_02], \n"
            + "\t[], [], [], \n"
            + "\t[cell_20], [cell_21], [], \n"
            + ")\n"
        )

    def test_convert_table_cell(self):
        cell = ast.TableCell(children=[ast.Text("Cell text")])

        result = cell.convert(self.typst_converter)

        assert result == "Cell text"

    def test_convert_task_list_item_checked(self):
        task_list_item = ast.TaskListItem(
            checked=True,
            children=[ast.Text("Task")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "\n[x] Task\n"

    def test_convert_task_list_item_unchecked(self):
        task_list_item = ast.TaskListItem(
            checked=False,
            children=[ast.Text("Task")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "\n[ ] Task\n"

    def test_convert_empty_task_list_item_unchecked(self):
        task_list_item = ast.TaskListItem(checked=False)

        result = task_list_item.convert(self.typst_converter)

        assert result == "\n[ ] \n"
