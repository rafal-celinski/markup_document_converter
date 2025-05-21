import pkgutil
import importlib
from types import ModuleType
from typing import Callable

from markup_document_converter.parsers.base_parser import BaseParser
from markup_document_converter.converters.base_converter import BaseConverter
from markup_document_converter import parsers, converters

_name_to_parser: dict[str, type[BaseParser]] = {}
_parser_to_names: dict[type[BaseParser], list[str]] = {}

_name_to_converter: dict[str, type[BaseConverter]] = {}
_converter_to_names: dict[type[BaseConverter], list[str]] = {}


def register_parser(*names: str) -> Callable[[type[BaseParser]], type[BaseParser]]:
    """
    Class decorator to register a parser under a primary name plus aliases.
    Usage:
        @register_parser("markdown", "md", "mkd")
        class MarkdownParser(BaseParser): ...
    """

    def decorator(cls: type[BaseParser]) -> type[BaseParser]:
        for name in names:
            key = name.lower()
            _name_to_parser[key] = cls
            _parser_to_names.setdefault(cls, [])
            if key not in _parser_to_names[cls]:
                _parser_to_names[cls].append(key)
        return cls

    return decorator


def register_converter(
    *names: str,
) -> Callable[[type[BaseConverter]], type[BaseConverter]]:
    """
    Class decorator to register a converter under a primary name plus aliases.
    Usage:
        @register_converter("latex", "tex")
        class LatexConverter(BaseConverter): ...
    """

    def decorator(cls: type[BaseConverter]) -> type[BaseConverter]:
        for name in names:
            key = name.lower()
            _name_to_converter[key] = cls
            _converter_to_names.setdefault(cls, [])
            if key not in _converter_to_names[cls]:
                _converter_to_names[cls].append(key)
        return cls

    return decorator


def get_parser(name: str) -> BaseParser:
    """
    Instantiate a parser by any of its registered names.
    """
    key = name.lower()
    try:
        return _name_to_parser[key]()
    except KeyError:
        raise ValueError(f"No parser registered for '{name}'")


def get_converter(name: str) -> BaseConverter:
    """
    Instantiate a converter by any of its registered names.
    """
    key = name.lower()
    try:
        return _name_to_converter[key]()
    except KeyError:
        raise ValueError(f"No converter registered for '{name}'")


def get_available_parsers() -> list[tuple[str, list[str]]]:
    """
    Returns a list of (primary_name, [alias1, alias2, ...]) tuples,
    sorted by primary_name.
    """
    out: list[tuple[str, list[str]]] = []
    for cls, names in _parser_to_names.items():
        primary = names[0]
        aliases = names[1:]
        out.append((primary, aliases))
    return sorted(out, key=lambda x: x[0])


def get_available_converters() -> list[tuple[str, list[str]]]:
    """
    Returns a list of (primary_name, [alias1, alias2, ...]) tuples,
    sorted by primary_name.
    """
    out: list[tuple[str, list[str]]] = []
    for cls, names in _converter_to_names.items():
        primary = names[0]
        aliases = names[1:]
        out.append((primary, aliases))
    return sorted(out, key=lambda x: x[0])


def _auto_import(pkg: ModuleType) -> None:
    """
    Dynamically import all submodules in the given package so
    that @register_* decorators actually run.
    """
    for finder, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        if name.startswith("_"):
            continue
        full = f"{pkg.__name__}.{name}"
        module = importlib.import_module(full)
        if is_pkg:
            _auto_import(module)


_auto_import(parsers)
_auto_import(converters)
