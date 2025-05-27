from pathlib import Path
import typer
from markup_document_converter.core import convert_document
from markup_document_converter.registry import (
    get_available_parsers,
    get_available_converters,
)
import os


app = typer.Typer(
    name="markup_document_converter",
    help="Convert Markdown into Typst or LaTeX via a universal AST.",
    add_completion=False,
)


@app.command("convert")
def convert(
    input: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the input file to convert (e.g. README.md)",
    ),
    to: str = typer.Option(
        ...,
        "--to",
        "-t",
        help="Target format. Choose from: " + ", ".join(get_available_converters()),
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        help="Where to write the result. If omitted, writes to stdout.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging of parsing and conversion steps.",
    ),
):
    """
    Read INPUT, parse it to the universal AST, then render as the chosen TARGET format.
    """

    input_path = str(input)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    content = get_content(input_path)

    _, ext = os.path.splitext(input_path)
    source_format = ext.lstrip(".").lower()

    result = convert_document(
        content=content,
        source_format=source_format,
        target_format=to.lower(),
    )

    if output:
        output.write_text(result, encoding="utf-8")
    else:
        typer.echo(result)


@app.command("list-formats")
def list_formats():
    """
    Show all supported input parsers and output converters.
    """
    typer.echo("Input parsers:")
    for p in get_available_parsers():
        typer.echo(f"  • {p}")

    typer.echo("\nOutput converters:")
    for c in get_available_converters():
        typer.echo(f"  • {c}")


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(None, "--version", help="Show version and exit."),
):
    """
    markup_document_converter — a universal-markup converter.
    """
    if version:
        from markup_document_converter import __version__

        typer.echo(f"markup_document_converter version {__version__}")
        raise typer.Exit()


def get_content(input_path: str) -> str:
    with open(input_path, "r") as fp:
        content = fp.read()
    if not content.endswith("\n"):
        content += "\n"
    return content


if __name__ == "__main__":
    app()
