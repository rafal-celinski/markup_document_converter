from pathlib import Path

import typer

from markup_document_converter.registry import (
    get_available_parsers,
    get_available_converters,
)
from markup_document_converter.core import convert_document

app = typer.Typer(
    name="markup_document_converter",
    help="Convert Markdown into Typst or LaTeX via a universal AST.",
    add_completion=False,
)


@app.command("list-formats")
def list_formats() -> None:
    """
    Show all supported input parsers and output converters,
    listing each primary name with its aliases.
    """
    typer.echo("Input parsers:")
    for primary, aliases in get_available_parsers():
        if aliases:
            typer.echo(f"  • {primary} (aliases: {', '.join(aliases)})")
        else:
            typer.echo(f"  • {primary}")

    typer.echo("\nOutput converters:")
    for primary, aliases in get_available_converters():
        if aliases:
            typer.echo(f"  • {primary} (aliases: {', '.join(aliases)})")
        else:
            typer.echo(f"  • {primary}")


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
        help="Target format. Choose from: "
        + ", ".join(name for name, _ in get_available_converters()),
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        help="Where to write the result. If omitted, writes to stdout.",
    ),
) -> None:
    """
    Read INPUT, parse it to the universal AST, then render as the chosen TARGET format.
    """
    try:
        content = input.read_text(encoding="utf-8")
        if not content.endswith("\n"):
            content += "\n"

        source_format = input.suffix.lstrip(".").lower()

        result = convert_document(
            content=content,
            source_format=source_format,
            target_format=to.lower(),
        )

        if output:
            output.write_text(result, encoding="utf-8")
        else:
            typer.echo(result)

    except ValueError as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    except FileNotFoundError as e:
        typer.secho(
            f"Error: Cannot save file to a non-existent directory.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Unexpected error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", help="Show version and exit."),
) -> None:
    """
    markup_document_converter — a universal-markup converter.
    """
    if version:
        from markup_document_converter import __version__

        typer.echo(f"markup_document_converter version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
