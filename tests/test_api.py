import pytest
from markup_document_converter.api import app as flask_app


class TestAPI:
    @pytest.fixture(autouse=True)
    def _patch_registry(self, monkeypatch):
        monkeypatch.setattr(
            "markup_document_converter.api.get_available_parsers", lambda: ["markdown"]
        )
        monkeypatch.setattr(
            "markup_document_converter.api.get_available_converters", lambda: ["typst"]
        )
        monkeypatch.setattr(
            "markup_document_converter.api.convert_document",
            lambda content, infmt, outfmt: f"converted:{content}",
        )

    @pytest.fixture
    def client(self):
        flask_app.config["TESTING"] = True
        with flask_app.test_client() as client:
            yield client

    def test_list_formats(self, client):
        result = client.get("/list-formats")
        assert result.status_code == 200
        data = result.get_json()
        assert data["inputFormats"] == ["markdown"]
        assert data["outputFormats"] == ["typst"]

    def test_convert_success(self, client):
        payload = {
            "inputFormat": "markdown",
            "outputFormat": "typst",
            "content": "content",
        }
        result = client.post("/convert", json=payload)

        assert result.status_code == 200
        assert result.get_json()["content"] == "converted:content"

    def test_convert_no_input_format(self, client):
        payload = {"outputFormat": "typst", "content": "content"}
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["inputFormat"] == "Missing key"

    def test_convert_no_output_format(self, client):
        payload = {"inputFormat": "markdown", "content": "content"}
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["outputFormat"] == "Missing key"

    def test_convert_no_content(self, client):
        payload = {
            "inputFormat": "markdown",
            "outputFormat": "typst",
        }
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["content"] == "Missing key"

    def test_convert_empty_payload(self, client):
        payload = {}
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["inputFormat"] == "Missing key"
        assert result.get_json()["outputFormat"] == "Missing key"
        assert result.get_json()["content"] == "Missing key"

    def test_convert_unsupported_input_format(self, client):
        payload = {
            "inputFormat": "unsupported",
            "outputFormat": "typst",
            "content": "content",
        }
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["inputFormat"] == "Unsupported format"

    def test_convert_unsupported_output_format(self, client):
        payload = {
            "inputFormat": "markdown",
            "outputFormat": "unsupported",
            "content": "content",
        }
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["outputFormat"] == "Unsupported format"

    def test_convert_unsupported_input_output_format(self, client):
        payload = {
            "inputFormat": "unsupported",
            "outputFormat": "unsupported",
            "content": "content",
        }
        result = client.post("/convert", json=payload)

        assert result.status_code == 400
        assert result.get_json()["inputFormat"] == "Unsupported format"
        assert result.get_json()["outputFormat"] == "Unsupported format"
