from typing import Type, Callable
import pkgutil
import importlib
from markup_document_converter.parsers.base_parser import BaseParser
from markup_document_converter.converters.base_converter import BaseConverter
from markup_document_converter import parsers, converters

_parsers: dict[str, type[BaseParser]] = {}
_converters: dict[str, type[BaseConverter]] = {}


def register_parser(name: str) -> Callable[[Type[BaseParser]], Type[BaseParser]]:
    """
    Class decorator to register a parser under `name`.

    Usage:

        @register_parser("md")
        @register_parser("markdown")
        class MarkdownParser(BaseParser): ...
    """

    def decorator(cls: Type[BaseParser]) -> Type[BaseParser]:
        _parsers[name.lower()] = cls
        return cls

    return decorator


def register_converter(
    name: str,
) -> Callable[[Type[BaseConverter]], Type[BaseConverter]]:
    """
    Class decorator to register a converter under `name`.

    Usage:

        @register_converter("typst")
        class TypstConverter(BaseConverter): ...
    """

    def decorator(cls: Type[BaseConverter]) -> Type[BaseConverter]:
        _converters[name.lower()] = cls
        return cls

    return decorator


def get_parser(name: str) -> BaseParser:
    """
    Look up and instantiate a parser by name.

    Args:
        name (str): Name of the parser to retrieve.

    Returns:
        BaseParser: An instance of the requested parser.

    Raises:
        ValueError: If no parser is registered under `name`.
    """
    key = name.lower()
    if key not in _parsers:
        raise ValueError(f"No parser registered for '{name}'")
    return _parsers[key]()


def get_converter(name: str) -> BaseConverter:
    """
    Look up and instantiate a converter by name.

    Args:
        name (str): Name of the converter to retrieve.

    Returns:
        BaseConverter: An instance of the requested converter.

    Raises:
        ValueError: If no converter is registered under `name`.
    """
    key = name.lower()
    if key not in _converters:
        raise ValueError(f"No converter registered for '{name}'")
    return _converters[key]()


def get_available_parsers() -> list[str]:
    """
    List all registered parser names.

    Returns:
        List[str]: Sorted list of parser keys.
    """
    return sorted(_parsers.keys())


def get_available_converters() -> list[str]:
    """
    List all registered converter names.

    Returns:
        List[str]: Sorted list of converter keys.
    """
    return sorted(_converters.keys())


def _auto_import(pkg) -> None:
    for finder, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"{pkg.__name__}.{name}")


_auto_import(parsers)
_auto_import(converters)
