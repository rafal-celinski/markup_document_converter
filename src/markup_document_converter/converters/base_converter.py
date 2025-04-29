from abc import ABC, abstractmethod
import markup_document_converter.ast as ast


class BaseConverter(ABC):
    @abstractmethod
    def convert_default(self, node: ast.ASTNode) -> str:
        pass

    @abstractmethod
    def convert_document(self, document: ast.Document) -> str:
        pass

    @abstractmethod
    def convert_heading(self, heading: ast.Heading) -> str:
        pass

    @abstractmethod
    def convert_bold(self, bold: ast.Bold) -> str:
        pass

    @abstractmethod
    def convert_italic(self, italic: ast.Italic) -> str:
        pass

    @abstractmethod
    def convert_strike(self, strike: ast.Strike) -> str:
        pass

    @abstractmethod
    def convert_text(self, text: ast.Text) -> str:
        pass

    @abstractmethod
    def convert_paragraph(self, paragraph: ast.Paragraph) -> str:
        pass

    @abstractmethod
    def convert_line_break(self, line_break: ast.LineBreak) -> str:
        pass

    @abstractmethod
    def convert_blockquote(self, blockquote: ast.Blockquote) -> str:
        pass

    @abstractmethod
    def convert_list(self, list_node: ast.List) -> str:
        pass

    @abstractmethod
    def convert_list_item(self, list_item: ast.ListItem) -> str:
        pass

    @abstractmethod
    def convert_code_block(self, code_block: ast.CodeBlock) -> str:
        pass

    @abstractmethod
    def convert_inline_code(self, inline_code: ast.InlineCode) -> str:
        pass

    @abstractmethod
    def convert_image(self, image: ast.Image) -> str:
        pass

    @abstractmethod
    def convert_link(self, link: ast.Link) -> str:
        pass

    @abstractmethod
    def convert_horizontal_rule(self, horizontal_rule: ast.HorizontalRule) -> str:
        pass

    @abstractmethod
    def convert_table(self, table: ast.Table) -> str:
        pass

    @abstractmethod
    def convert_table_row(self, table_row: ast.TableRow) -> str:
        pass

    @abstractmethod
    def convert_table_cell(self, table_cell: ast.TableCell) -> str:
        pass

    @abstractmethod
    def convert_task_list_item(self, task_list_item: ast.TaskListItem) -> str:
        pass
