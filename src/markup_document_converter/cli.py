from pathlib import Path
import sys
from typing import Optional

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


@app.command("webapp")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(5000, "--port", "-p", help="Port to listen on"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
) -> None:
    """
    Run the Flask web-app.
    """
    from markup_document_converter.webapp import app as flask_app

    flask_app.run(host=host, port=port, debug=debug)


@app.command("convert")
def convert(
    input: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the input file to convert (e.g. README.md). Omit to read from stdin.",
    ),
    from_format: Optional[str] = typer.Option(
        None,
        "--from-format",
        "-f",
        help="When reading from stdin, the input format (e.g. 'markdown').",
    ),
    to: str = typer.Option(
        ...,
        "--to",
        "-t",
        help="Target format. Choose from: "
        + ", ".join(name for name, _ in get_available_converters()),
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        help="Where to write the result. If omitted, writes to stdout.",
    ),
) -> None:
    """
    Read from a file or stdin, parse to the universal AST, then render as the chosen TARGET format.
    """
    read_from_stdin = input is None or str(input) == "-"
    read_from_file = not read_from_stdin

    if read_from_file and not sys.stdin.isatty():
        first_char = sys.stdin.read(1)
        if first_char:
            typer.secho(
                "Error: Cannot read from both file and stdin; please provide only one source.",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
        try:
            sys.stdin.seek(0)
        except Exception:
            pass

    if read_from_stdin:
        if not from_format:
            typer.secho(
                "Error: Reading from stdin requires --from-format/-f.",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
        content = sys.stdin.read()
        source_format = from_format.lower()
    else:
        content = input.read_text(encoding="utf-8")
        source_format = input.suffix.lstrip(".").lower()

    if not content.endswith("\n"):
        content += "\n"

    try:
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

    except FileNotFoundError:
        typer.secho(
            "Error: Cannot save file to a non-existent directory.",
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
