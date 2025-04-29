from abc import ABC, abstractmethod
import markup_document_converter.ast as ast


class BaseConverter(ABC):
    @abstractmethod
    def convert_default(self, node: ast.ASTNode):
        pass

    @abstractmethod
    def convert_document(self, document: ast.Document):
        pass

    @abstractmethod
    def convert_heading(self, heading: ast.Heading):
        pass

    @abstractmethod
    def convert_bold(self, bold: ast.Bold):
        pass

    @abstractmethod
    def convert_italic(self, italic: ast.Italic):
        pass

    @abstractmethod
    def convert_strike(self, strike: ast.Strike):
        pass

    @abstractmethod
    def convert_text(self, text: ast.Text):
        pass

    @abstractmethod
    def convert_paragraph(self, paragraph: ast.Paragraph):
        pass

    @abstractmethod
    def convert_line_break(self, line_break: ast.LineBreak):
        pass

    @abstractmethod
    def convert_blockquote(self, blockquote: ast.Blockquote):
        pass

    @abstractmethod
    def convert_list(self, list_node: ast.List):
        pass

    @abstractmethod
    def convert_list_item(self, list_item: ast.ListItem):
        pass

    @abstractmethod
    def convert_code_block(self, code_block: ast.CodeBlock):
        pass

    @abstractmethod
    def convert_inline_code(self, inline_code: ast.InlineCode):
        pass

    @abstractmethod
    def convert_image(self, image: ast.Image):
        pass

    @abstractmethod
    def convert_link(self, link: ast.Link):
        pass

    @abstractmethod
    def convert_horizontal_rule(self, horizontal_rule: ast.HorizontalRule):
        pass

    @abstractmethod
    def convert_table(self, table: ast.Table):
        pass

    @abstractmethod
    def convert_table_row(self, table_row: ast.TableRow):
        pass

    @abstractmethod
    def convert_table_cell(self, table_cell: ast.TableCell):
        pass

    @abstractmethod
    def convert_task_list_item(self, task_list_item: ast.TaskListItem):
        pass
