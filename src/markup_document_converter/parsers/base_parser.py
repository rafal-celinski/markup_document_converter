from abc import ABC, abstractmethod
from markup_document_converter.ast import ASTNode


class BaseParser(ABC):
    @abstractmethod
    def to_AST(self, input_file: str) -> ASTNode:
        """
        Parse input file to universal AST tree.

        Args:
            input_file (str): Path to the input file

        Returns:
            ASTNode: The root of the generated abstract syntax tree
        """
        pass
