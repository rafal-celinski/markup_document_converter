from abc import ABC, abstractmethod
import markup_document_converter.ast_tree as ast_tree


class BaseConverter(ABC):
    @abstractmethod
    def convert_default(self, node: ast_tree.ASTNode) -> str:
        pass

    @abstractmethod
    def convert_document(self, document: ast_tree.Document) -> str:
        pass

    @abstractmethod
    def convert_heading(self, heading: ast_tree.Heading) -> str:
        pass

    @abstractmethod
    def convert_bold(self, bold: ast_tree.Bold) -> str:
        pass

    @abstractmethod
    def convert_italic(self, italic: ast_tree.Italic) -> str:
        pass

    @abstractmethod
    def convert_strike(self, strike: ast_tree.Strike) -> str:
        pass

    @abstractmethod
    def convert_text(self, text: ast_tree.Text) -> str:
        pass

    @abstractmethod
    def convert_paragraph(self, paragraph: ast_tree.Paragraph) -> str:
        pass

    @abstractmethod
    def convert_line_break(self, line_break: ast_tree.LineBreak) -> str:
        pass

    @abstractmethod
    def convert_blockquote(self, blockquote: ast_tree.Blockquote) -> str:
        pass

    @abstractmethod
    def convert_list(self, list_node: ast_tree.List) -> str:
        pass

    @abstractmethod
    def convert_list_item(self, list_item: ast_tree.ListItem) -> str:
        pass

    @abstractmethod
    def convert_code_block(self, code_block: ast_tree.CodeBlock) -> str:
        pass

    @abstractmethod
    def convert_inline_code(self, inline_code: ast_tree.InlineCode) -> str:
        pass

    @abstractmethod
    def convert_image(self, image: ast_tree.Image) -> str:
        pass

    @abstractmethod
    def convert_link(self, link: ast_tree.Link) -> str:
        pass

    @abstractmethod
    def convert_horizontal_rule(self, horizontal_rule: ast_tree.HorizontalRule) -> str:
        pass

    @abstractmethod
    def convert_table(self, table: ast_tree.Table) -> str:
        pass

    @abstractmethod
    def convert_table_row(self, table_row: ast_tree.TableRow) -> str:
        pass

    @abstractmethod
    def convert_table_cell(self, table_cell: ast_tree.TableCell) -> str:
        pass

    @abstractmethod
    def convert_task_list_item(self, task_list_item: ast_tree.TaskListItem) -> str:
        pass
