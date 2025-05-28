from flask import Flask, jsonify, request, render_template

from markup_document_converter.registry import (
    get_available_parsers,
    get_available_converters,
)

from markup_document_converter.core import convert_document

app = Flask(__name__)


@app.route("/api/list-formats", methods=["GET"])
def list_formats():
    """
    Return all supported input parsers and output converters.

    This endpoint provides a list of all available document formats
    that can be used for parsing input documents and converting to output formats.

    Returns:
        tuple: A JSON response containing:
            - inputFormats (list): Available input parser formats
            - outputFormats (list): Available output converter formats
        And HTTP status code 200.

    Example:
        GET /api/list-formats

        Response:
        {
            "inputFormats": ["markdown", "html"],
            "outputFormats": ["typst", "html", "latex"]
        }
    """
    parsers = [primary for primary, _ in get_available_parsers()]
    converters = [primary for primary, _ in get_available_converters()]

    return jsonify({"inputFormats": parsers, "outputFormats": converters}), 200


@app.route("/api/convert", methods=["POST"])
def convert():
    """
    Convert document content from one format to another.

    This endpoint accepts document content in a specified input format
    and converts it to the requested output format using the registered
    parsers and converters.

    Expected JSON payload:
        inputFormat (str): The format of the input content
        outputFormat (str): The desired output format
        content (str): The document content to convert

    Returns:
        tuple: A JSON response containing either:
            - On success (200): {"content": converted_content}
            - On validation error (400): Error dictionary with field-specific messages

    Example:
        POST /api/convert
        {
            "inputFormat": "markdown",
            "outputFormat": "typst",
            "content": "# Hello World"
        }

        Response:
        {
            "content": "= Hello World"
        }
    """
    data = request.get_json() or {}
    input_format = data.get("inputFormat")
    output_format = data.get("outputFormat")
    content = data.get("content")

    error_dict = {}

    if not input_format:
        error_dict["inputFormat"] = "Missing key"
    if not output_format:
        error_dict["outputFormat"] = "Missing key"
    if not content:
        error_dict["content"] = "Missing key"

    if len(error_dict) > 0:
        return jsonify(error_dict), 400

    input_format = input_format.lower()
    output_format = output_format.lower()

    parsers = [primary for primary, _ in get_available_parsers()]
    converters = [primary for primary, _ in get_available_converters()]

    if input_format not in parsers:
        error_dict["inputFormat"] = "Unsupported format"

    if output_format not in converters:
        error_dict["outputFormat"] = "Unsupported format"

    if len(error_dict) > 0:
        return jsonify(error_dict), 400

    result = convert_document(content, input_format, output_format)

    return jsonify({"content": result}), 200


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Serve the main web interface for document conversion.

    This endpoint provides both the web form interface and handles
    form submissions for document conversion. On GET requests, it displays
    the conversion form. On POST requests, it processes the form data
    and returns the converted content.

    Form fields (POST):
        sourceTextArea (str): The source document content
        inputFormats (str): Selected input format
        outputFormats (str): Selected output format

    Returns:
        str: Rendered HTML template with:
            - input_formats: List of available input formats
            - output_formats: List of available output formats
            - result: Converted content (only on POST with valid data)

    Template Variables:
        input_formats (list): Available input parser formats
        output_formats (list): Available output converter formats
        result (str or None): Conversion result or None for GET requests
    """
    parsers = [primary for primary, _ in get_available_parsers()]
    converters = [primary for primary, _ in get_available_converters()]

    result = None

    if request.method == "POST":
        content = request.form["sourceTextArea"]
        input_format = request.form["inputFormats"]
        output_format = request.form["outputFormats"]
        result = convert_document(content, input_format, output_format)
        print(content)

    return render_template(
        "index.html", input_formats=parsers, output_formats=converters, result=result
    )
