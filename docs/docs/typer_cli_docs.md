# `CLI App`

Convert Markdown into Typst or LaTeX via a universal AST.

**Usage**:

```console
$ markup_document_converter [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show version and exit.
* `--help`: Show this message and exit.

**Commands**:

* `list-formats`: Show all supported input parsers and output converters,
    listing each primary name with its aliases.
* `webapp`: Run the Flask web-app.
* `convert`: Read from a file or stdin, parse to the universal AST, then render as the chosen TARGET format.

## `markup_document_converter list-formats`

Show all supported input parsers and output converters,
listing each primary name with its aliases.

**Usage**:

```console
$ markup_document_converter list-formats [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `markup_document_converter webapp`

Run the Flask web-app.

**Usage**:

```console
$ markup_document_converter webapp [OPTIONS]
```

**Options**:

* `-h, --host TEXT`: Host to bind to  [default: 127.0.0.1]
* `-p, --port INTEGER`: Port to listen on  [default: 5000]
* `-d, --debug`: Enable debug mode
* `--help`: Show this message and exit.

## `markup_document_converter convert`

Read from a file or stdin, parse to the universal AST, then render as the chosen TARGET format.

**Usage**:

```console
$ markup_document_converter convert [OPTIONS] [INPUT]
```

**Arguments**:

* `[INPUT]`: Path to the input file to convert (e.g. README.md). Omit to read from stdin.

**Options**:

* `-f, --from-format TEXT`: When reading from stdin, the input format (e.g. &#x27;markdown&#x27;).
* `-t, --to TEXT`: Target format. Choose from: latex, typst  [required]
* `-o, --output FILE`: Where to write the result. If omitted, writes to stdout.
* `--help`: Show this message and exit.
