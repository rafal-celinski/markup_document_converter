from abc import ABC, abstractmethod
from markup_document_converter.ast import ASTNode


class BaseConverter(ABC):
    @abstractmethod
    def to_AST(self, input_file: str) -> ASTNode:
        """
        Convert input file to universal AST tree.

        Args:
            input_file (str): Path to the input file

        Returns:
            ASTNode: The root of the generated abstract syntax tree
        """
        pass

    @abstractmethod
    def to_file(self, ast_root: ASTNode) -> None:
        """
        Convert abstract syntax tree to a file of converter type

        Args:
            ast_root (ASTNode): The root of the abstract syntax tree

        Returns:
            None: Creates file
        """
        pass
