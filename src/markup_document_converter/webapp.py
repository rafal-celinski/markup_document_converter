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
    """

    parsers = [primary for primary, _ in get_available_parsers()]
    converters = [primary for primary, _ in get_available_converters()]

    return jsonify({"inputFormats": parsers, "outputFormats": converters}), 200


@app.route("/api/convert", methods=["POST"])
def convert():
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


def main():
    app.run(debug=True)
