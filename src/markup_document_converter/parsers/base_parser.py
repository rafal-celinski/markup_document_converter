from abc import ABC, abstractmethod
from markup_document_converter.ast import Document


class BaseParser(ABC):
    @abstractmethod
    def to_AST(self, content: str) -> Document:
        """
        Parse input content string to universal AST tree.

        Args:
            content (str): The full markup content as a single string.

        Returns:
            Document: The root of the generated abstract syntax tree.
        """
        pass
