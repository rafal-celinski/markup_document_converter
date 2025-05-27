import markup_document_converter.ast_tree as ast_tree
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
        document = ast_tree.Document(
            children=[
                ast_tree.Heading(
                    level=1,
                    children=[ast_tree.Text("Heading 1")],
                ),
                ast_tree.Text("Text "),
                ast_tree.Bold(
                    children=[
                        ast_tree.Text("Bold text"),
                    ]
                ),
            ]
        )

        result = document.convert(self.typst_converter)

        assert result == "\n" "= Heading 1\n" "Text *Bold text*\n"

    def test_empty_document(self):
        document = ast_tree.Document([])
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
        heading = ast_tree.Heading(
            level=level,
            children=[ast_tree.Text("Heading")],
        )

        result = heading.convert(self.typst_converter)

        assert result == expected

    def test_empty_heading(self):
        heading = ast_tree.Heading(level=1)

        result = heading.convert(self.typst_converter)

        assert result == "\n= \n"

    def test_convert_bold(self):
        bold = ast_tree.Bold(children=[ast_tree.Text("Bold text")])

        result = bold.convert(self.typst_converter)

        assert result == "*Bold text*"

    def test_bold_empty(self):
        bold = ast_tree.Bold([])
        result = bold.convert(self.typst_converter)
        assert result == "**"

    def test_convert_italic(self):
        italic = ast_tree.Italic(children=[ast_tree.Text("Italic text")])

        result = italic.convert(self.typst_converter)

        assert result == "_Italic text_"

    def test_empty_italic(self):
        italic = ast_tree.Italic()

        result = italic.convert(self.typst_converter)

        assert result == "__"

    def test_convert_strike(self):
        strike = ast_tree.Strike(children=[ast_tree.Text("Strike text")])

        result = strike.convert(self.typst_converter)

        assert result == "#strike[Strike text]"

    def test_empty_strike(self):
        strike = ast_tree.Strike()

        result = strike.convert(self.typst_converter)

        assert result == "#strike[]"

    def test_convert_text(self):
        text = ast_tree.Text("Text")

        result = text.convert(self.typst_converter)

        assert result == "Text"

    def test_convert_text_with_special_chars(self):
        text = ast_tree.Text("*#[]+-/$=\\<>@'\"`")

        result = text.convert(self.typst_converter)

        assert result == "\\*\\#\\[\\]\\+\\-\\/\\$\\=\\\\\\<\\>\\@\\'\\\"\\`"

    def test_convert_text_with_unusual_special_chars(self):
        text = ast_tree.Text("_ | _| _ |_")

        result = text.convert(self.typst_converter)

        assert result == "\\_ | \\_| \\_ |_"

    def test_convert_paragraph(self):
        paragraph = ast_tree.Paragraph(children=[ast_tree.Text("Paragraph")])

        result = paragraph.convert(self.typst_converter)

        assert result == "\nParagraph\n"

    def test_empty_paragraph(self):
        paragraph = ast_tree.Paragraph()

        result = paragraph.convert(self.typst_converter)

        assert result == "\n\n"

    def test_convert_line_break(self):
        line_break = ast_tree.LineBreak()

        result = line_break.convert(self.typst_converter)

        assert result == "\\ "

    def test_convert_blockquote(self):
        blockquote = ast_tree.Blockquote(children=[ast_tree.Text("Blockquote")])

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Blockquote]"

    def test_empty_blockquote(self):
        blockquote = ast_tree.Blockquote()

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[]"

    def test_nested_blockquote(self):
        blockquote = ast_tree.Blockquote(
            children=[
                ast_tree.Text("Blockquote "),
                ast_tree.Blockquote(children=[ast_tree.Text("Nested Blockquote")]),
            ]
        )

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Blockquote #quote[Nested Blockquote]]"

    def test_convert_ordered_list(self):
        ordered_list = ast_tree.List(
            list_type="ordered",
            children=[
                ast_tree.ListItem(
                    order=1,
                    children=[ast_tree.Text("Item 1")],
                ),
                ast_tree.ListItem(
                    order=2,
                    children=[ast_tree.Text("Item 2")],
                ),
                ast_tree.ListItem(
                    order=3,
                    children=[ast_tree.Text("Item 3")],
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n1. Item 1\n" + "2. Item 2\n" + "3. Item 3\n"

    def test_convert_autoordered_list(self):
        ordered_list = ast_tree.List(
            list_type="ordered",
            children=[
                ast_tree.ListItem(children=[ast_tree.Text("Item 1")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 2")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 3")]),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n+ Item 1\n" + "+ Item 2\n" + "+ Item 3\n"

    def test_convert_unordered_list(self):
        unordered_list = ast_tree.List(
            list_type="unordered",
            children=[
                ast_tree.ListItem(children=[ast_tree.Text("Item 1")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 2")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 3")]),
            ],
        )

        result = unordered_list.convert(self.typst_converter)

        assert result == "\n- Item 1\n" + "- Item 2\n" + "- Item 3\n"

    def test_convert_ordered_list_with_task(self):
        ordered_list = ast_tree.List(
            list_type="ordered",
            children=[
                ast_tree.ListItem(
                    order=1,
                    children=[ast_tree.Text("Item 1")],
                ),
                ast_tree.ListItem(
                    order=2,
                    children=[ast_tree.Text("Item 2")],
                ),
                ast_tree.TaskListItem(
                    order=3,
                    checked=False,
                    children=[ast_tree.Text("Task 1")],
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n1. Item 1\n" + "2. Item 2\n" + "3. [ ] Task 1\n"

    def test_convert_unordered_list_with_task(self):
        ordered_list = ast_tree.List(
            list_type="unordered",
            children=[
                ast_tree.ListItem(
                    children=[ast_tree.Text("Item 1")],
                ),
                ast_tree.ListItem(
                    children=[ast_tree.Text("Item 2")],
                ),
                ast_tree.TaskListItem(
                    checked=False,
                    children=[ast_tree.Text("Task 1")],
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n- Item 1\n" + "- Item 2\n" + "- [ ] Task 1\n"

    def test_convert_nested_list(self):
        nested_list = ast_tree.List(
            list_type="unordered",
            children=[
                ast_tree.ListItem(children=[ast_tree.Text("Item 1")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 2")]),
                ast_tree.ListItem(children=[ast_tree.Text("Item 3")]),
                ast_tree.ListItem(
                    children=[
                        ast_tree.Text("Item 4"),
                        ast_tree.List(
                            list_type="unordered",
                            children=[
                                ast_tree.ListItem(children=[ast_tree.Text("Item 4a")]),
                                ast_tree.ListItem(children=[ast_tree.Text("Item 4b")]),
                                ast_tree.ListItem(children=[ast_tree.Text("Item 4c")]),
                            ],
                        ),
                        ast_tree.Text("some additional text"),
                    ]
                ),
                ast_tree.ListItem(children=[ast_tree.Text("Item 5")]),
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
        ordered_list = ast_tree.List("ordered")

        result = ordered_list.convert(self.typst_converter)

        assert result == "\n"

    def test_convert_list_item_single_text(self):
        list_item = ast_tree.ListItem(children=[ast_tree.Text("Item")])

        result = list_item.convert(self.typst_converter)

        assert result == "Item\n"

    def test_convert_list_item_multiple_text(self):
        list_item = ast_tree.ListItem(
            children=[
                ast_tree.Bold(children=[ast_tree.Text("Bold")]),
                ast_tree.Text(" Item"),
            ]
        )

        result = list_item.convert(self.typst_converter)

        assert result == "*Bold* Item\n"

    def test_convert_list_item_indent_list(self):
        list_item = ast_tree.ListItem(
            children=[
                ast_tree.Text("Item"),
                ast_tree.List(
                    list_type="unordered",
                    children=[
                        ast_tree.ListItem(children=[ast_tree.Text("Indent item")])
                    ],
                ),
            ]
        )

        result = list_item.convert(self.typst_converter)

        assert result == "Item\n" + "- Indent item\n"

    def test_convert_empty_list_item(self):
        list_item = ast_tree.ListItem()

        result = list_item.convert(self.typst_converter)

        assert result == "\n"

    def test_convert_task_list_item_checked(self):
        task_list_item = ast_tree.TaskListItem(
            checked=True,
            children=[ast_tree.Text("Task")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "[x] Task\n"

    def test_convert_task_list_item_unchecked(self):
        task_list_item = ast_tree.TaskListItem(
            checked=False,
            children=[ast_tree.Text("Task")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "[ ] Task\n"

    def test_convert_empty_task_list_item_unchecked(self):
        task_list_item = ast_tree.TaskListItem(checked=False)

        result = task_list_item.convert(self.typst_converter)

        assert result == "[ ] \n"

    def test_convert_code_block(self):
        code_block = ast_tree.CodeBlock(language="python", code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```python\nprint('Hello World!')\n```"

    def test_code_block_without_language(self):
        code_block = ast_tree.CodeBlock(code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```\nprint('Hello World!')\n```"

    def test_convert_inline_code(self):
        inline_code = ast_tree.InlineCode(
            language="python", code="print('Hello World!')"
        )

        result = inline_code.convert(self.typst_converter)

        assert result == "```python print('Hello World!')```"

    def test_convert_inline_code_without_language(self):
        inline_code = ast_tree.InlineCode(code="print('Hello World!')")

        result = inline_code.convert(self.typst_converter)

        assert result == "```print('Hello World!')```"

    def test_convert_image(self):
        image = ast_tree.Image(source="image.png", alt_text="example image")

        result = image.convert(self.typst_converter)

        assert result == '#image("image.png", alt: "example image")'

    def test_convert_image_without_alt(self):
        image = ast_tree.Image(source="image.png")

        result = image.convert(self.typst_converter)

        assert result == '#image("image.png")'

    def test_convert_link_with_text(self):
        link = ast_tree.Link(
            source="example.com",
            children=[ast_tree.Text("Link text")],
        )

        result = link.convert(self.typst_converter)

        assert result == '#link("example.com")[Link text]'

    def test_convert_link_with_formated_text(self):
        link = ast_tree.Link(
            source="example.com",
            children=[
                ast_tree.Bold(
                    children=[
                        ast_tree.Text("Bold"),
                    ]
                ),
                ast_tree.Text(", "),
                ast_tree.Italic(
                    children=[
                        ast_tree.Text("Italic"),
                    ]
                ),
                ast_tree.Text(" link text"),
            ],
        )

        result = link.convert(self.typst_converter)

        assert result == '#link("example.com")[*Bold*, _Italic_ link text]'

    def test_convert_link_without_text(self):
        link = ast_tree.Link(source="example.com")

        result = link.convert(self.typst_converter)

        assert result == '#link("example.com")'

    def test_convert_horizontal_rule(self):
        hr = ast_tree.HorizontalRule()

        result = hr.convert(self.typst_converter)

        assert result == "#line(length: 100%)"

    def test_convert_table_with_header(self):
        table = ast_tree.Table(
            children=[
                ast_tree.TableRow(
                    is_header=True,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_00")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_01")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_02")]),
                    ],
                ),
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_10")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_11")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_12")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_13")]),
                    ],
                ),
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_20")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_21")]),
                    ],
                ),
            ]
        )

        result = table.convert(self.typst_converter)

        assert (
            result
            == "\n#table(\n"
            + "\tcolumns: 4,\n"
            + "\ttable.header([cell_00], [cell_01], [cell_02], ),\n"
            + "\t[cell_10], [cell_11], [cell_12], [cell_13], \n"
            + "\t[cell_20], [cell_21], [], [], \n"
            + ")\n"
        )

    def test_convert_table_without_header(self):
        table = ast_tree.Table(
            children=[
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_00")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_01")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_02")]),
                    ],
                ),
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_10")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_11")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_12")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_13")]),
                    ],
                ),
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_20")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_21")]),
                    ],
                ),
            ]
        )

        result = table.convert(self.typst_converter)

        assert (
            result
            == "\n#table(\n"
            + "\tcolumns: 4,\n"
            + "\t[cell_00], [cell_01], [cell_02], [], \n"
            + "\t[cell_10], [cell_11], [cell_12], [cell_13], \n"
            + "\t[cell_20], [cell_21], [], [], \n"
            + ")\n"
        )

    def test_convert_empty_table(self):
        table = ast_tree.Table()

        result = table.convert(self.typst_converter)

        assert result == "\n#table(\n" + "\tcolumns: 0,\n" + ")\n"

    def test_convert_table_empty_row(self):
        table = ast_tree.Table(
            children=[
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_00")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_01")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_02")]),
                    ],
                ),
                ast_tree.TableRow(is_header=False),
                ast_tree.TableRow(
                    is_header=False,
                    children=[
                        ast_tree.TableCell(children=[ast_tree.Text("cell_20")]),
                        ast_tree.TableCell(children=[ast_tree.Text("cell_21")]),
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

    def test_convert_table_row(self):
        row = ast_tree.TableRow(
            is_header=False,
            children=[
                ast_tree.TableCell(children=[ast_tree.Text("cell_0")]),
                ast_tree.TableCell(children=[ast_tree.Text("cell_1")]),
            ],
        )

        result = row.convert(self.typst_converter)

        assert result == "[cell_0], [cell_1], "

    def test_convert_table_row_header(self):
        row = ast_tree.TableRow(
            is_header=True,
            children=[
                ast_tree.TableCell(children=[ast_tree.Text("cell_0")]),
                ast_tree.TableCell(children=[ast_tree.Text("cell_1")]),
            ],
        )

        result = row.convert(self.typst_converter)

        assert result == "table.header([cell_0], [cell_1], ),"

    def test_convert_table_cell(self):
        cell = ast_tree.TableCell(children=[ast_tree.Text("Cell text")])

        result = cell.convert(self.typst_converter)

        assert result == "Cell text"
