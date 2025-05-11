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
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ],
                ),
                ast.Text("Curabitur hendrerit est sed velit molestie maximus"),
                ast.Bold(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus"),
                    ]
                ),
            ]
        )

        result = document.convert(self.typst_converter)

        assert (
            result == "\n"
            "= Curabitur hendrerit est sed velit molestie maximus\n"
            "Curabitur hendrerit est sed velit molestie maximus"
            "*Curabitur hendrerit est sed velit molestie maximus*\n"
        )

    @pytest.mark.parametrize(
        "level,expected",
        [
            (1, "\n= Curabitur hendrerit est sed velit molestie maximus\n"),
            (2, "\n== Curabitur hendrerit est sed velit molestie maximus\n"),
            (3, "\n=== Curabitur hendrerit est sed velit molestie maximus\n"),
            (4, "\n==== Curabitur hendrerit est sed velit molestie maximus\n"),
            (5, "\n===== Curabitur hendrerit est sed velit molestie maximus\n"),
            (6, "\n====== Curabitur hendrerit est sed velit molestie maximus\n"),
        ],
    )
    def test_convert_heading(self, level, expected):
        heading = ast.Heading(
            level=level,
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")],
        )

        result = heading.convert(self.typst_converter)

        assert result == expected

    def test_convert_bold(self):
        bold = ast.Bold(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = bold.convert(self.typst_converter)

        assert result == "*Curabitur hendrerit est sed velit molestie maximus*"

    def test_convert_italic(self):
        italic = ast.Italic(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = italic.convert(self.typst_converter)

        assert result == "_Curabitur hendrerit est sed velit molestie maximus_"

    def test_convert_strike(self):
        strike = ast.Strike(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = strike.convert(self.typst_converter)

        assert result == "#strike[Curabitur hendrerit est sed velit molestie maximus]"

    def test_convert_text(self):
        text = ast.Text("Curabitur hendrerit est sed velit molestie maximus")

        result = text.convert(self.typst_converter)

        assert result == "Curabitur hendrerit est sed velit molestie maximus"

    def test_convert_paragraph(self):
        paragraph = ast.Paragraph(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = paragraph.convert(self.typst_converter)

        assert result == "\nCurabitur hendrerit est sed velit molestie maximus\n"

    def test_convert_line_break(self):
        line_break = ast.LineBreak()

        result = line_break.convert(self.typst_converter)

        assert result == "\\ "

    def test_convert_blockquote(self):
        blockquote = ast.Blockquote(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = blockquote.convert(self.typst_converter)

        assert result == "#quote[Curabitur hendrerit est sed velit molestie maximus]"

    def test_convert_ordered_list(self):
        ordered_list = ast.List(
            list_type="ordered",
            children=[
                ast.ListItem(
                    order=1,
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ],
                ),
                ast.ListItem(
                    order=2,
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ],
                ),
                ast.ListItem(
                    order=3,
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ],
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert (
            result
            == "\n1. Curabitur hendrerit est sed velit molestie maximus\n"
            + "2. Curabitur hendrerit est sed velit molestie maximus\n"
            + "3. Curabitur hendrerit est sed velit molestie maximus\n"
        )

    def test_convert_autoordered_list(self):
        ordered_list = ast.List(
            list_type="ordered",
            children=[
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
            ],
        )

        result = ordered_list.convert(self.typst_converter)

        assert (
            result
            == "\n+ Curabitur hendrerit est sed velit molestie maximus\n"
            + "+ Curabitur hendrerit est sed velit molestie maximus\n"
            + "+ Curabitur hendrerit est sed velit molestie maximus\n"
        )

    def test_convert_unordered_list(self):
        unordered_list = ast.List(
            list_type="unordered",
            children=[
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
                ast.ListItem(
                    children=[
                        ast.Text("Curabitur hendrerit est sed velit molestie maximus")
                    ]
                ),
            ],
        )

        result = unordered_list.convert(self.typst_converter)

        assert (
            result
            == "\n- Curabitur hendrerit est sed velit molestie maximus\n"
            + "- Curabitur hendrerit est sed velit molestie maximus\n"
            + "- Curabitur hendrerit est sed velit molestie maximus\n"
        )

    def test_convert_list_item(self):
        list_item = ast.ListItem(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = list_item.convert(self.typst_converter)

        assert result == "Curabitur hendrerit est sed velit molestie maximus"

    def test_convert_code_block(self):
        code_block = ast.CodeBlock(language="python", code="print('Hello World!')")

        result = code_block.convert(self.typst_converter)

        assert result == "```python\nprint('Hello World!')\n```"

    def test_convert_inline_code(self):
        inline_code = ast.InlineCode(language="python", code="print('Hello World!')")

        result = inline_code.convert(self.typst_converter)

        assert result == "```python print('Hello World!')```"

    def test_convert_image(self):
        image = ast.Image(source="image.png", alt_text="example image")

        result = image.convert(self.typst_converter)

        assert result == '#image("image.png", alt: "example image")'

    def test_convert_link_with_text(self):
        link = ast.Link(
            source="example.com",
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")],
        )

        result = link.convert(self.typst_converter)

        assert (
            result
            == '#link("example.com")[Curabitur hendrerit est sed velit molestie maximus]'
        )

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

    def test_convert_table_cell(self):
        cell = ast.TableCell(
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")]
        )

        result = cell.convert(self.typst_converter)

        assert result == "Curabitur hendrerit est sed velit molestie maximus"

    def test_convert_task_list_item_checked(self):
        task_list_item = ast.TaskListItem(
            checked=True,
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "\n[x] Curabitur hendrerit est sed velit molestie maximus\n"

    def test_convert_task_list_item_unchecked(self):
        task_list_item = ast.TaskListItem(
            checked=False,
            children=[ast.Text("Curabitur hendrerit est sed velit molestie maximus")],
        )

        result = task_list_item.convert(self.typst_converter)

        assert result == "\n[ ] Curabitur hendrerit est sed velit molestie maximus\n"
