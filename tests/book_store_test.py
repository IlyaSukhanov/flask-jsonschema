# -*- coding: utf-8 -*-
import os
import unittest
from uuid import uuid4
import json

import pytest

from flask import Flask, jsonify


from flask_oasschema import (
    OASSchema,
    validate_request,
    validate_response,
    ValidationError,
    ValidationResponseError,
)

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["OAS_FILE"] = os.path.join(app.root_path, "schemas", "oas.json")
jsonschema = OASSchema(
    app, response_emit_warning=False, response_emit_error=False, response_emit_log=False
)

book = {
    "title": "Униженные и оскорблённые",
    "author": "Фёдор Михайлович Достоевский",
    "isbn": "978-1-84749-045-2",
}


@app.route("/books/<isbn>", methods=["PUT"])
@validate_request()
@validate_response(emit_error=True, emit_warning=False)
def book_put(isbn):
    if isbn == "bad":
        return jsonify({"foo": "bar"}), 201
    return jsonify({"status": "success", "uuid": str(uuid4())}), 201


@app.route("/books/id/<book_uuid>", methods=["GET"])
@validate_request()
def book_get_by_id(book_uuid):
    return "success"


@app.route("/health", methods=["GET"])
@validate_request()
@validate_response(emit_error=True)
def book_get_health():
    return "OK"


@app.route("/health", methods=["POST"])
@validate_request()
def book_post_health():
    return "OK"


@app.route("/books/by-author", methods=["GET"])
@validate_request()
def books_get_author():
    return "success"


@app.route("/books/by-title", methods=["GET"])
@validate_request()
@validate_response(emit_error=True)
def books_get_title():
    return jsonify([book]), 200


@app.route("/books/by-author/<author>", methods=["GET"])
@validate_request()
def books_by_author_and_title_filter(author):
    return "success"


@app.route("/no-response-schema", methods=["GET"])
@validate_response(emit_error=True)
def no_response_schema():
    return "OK"


@app.route("/no-response-schema-no-raise", methods=["GET"])
@validate_response()
def no_response_schema_no_raise():
    return "OK"


@app.route("/no-default-response-schema", methods=["GET"])
@validate_response(emit_error=True)
def no_default_response_schema():
    return "OK", 400


@app.route("/emit-all", methods=["GET"])
@validate_response(emit_error=True, emit_warning=True, emit_log=True)
def emit_all():
    return "OK", 400


@app.errorhandler(ValidationError)
def on_request_error(e):
    return f"error {e}", 400


@app.errorhandler(ValidationResponseError)
def on_response_error(e):
    return f"error {e}", 500


client = app.test_client()


class JsonSchemaTests(unittest.TestCase):
    def test_valid_json_put(self):
        r = client.put(
            "/books/0-330-25864-8",
            content_type="application/json",
            data=json.dumps(
                {
                    "title": "The Hitchhiker's Guide to the Galaxy",
                    "author": "Douglas  Adams",
                }
            ),
        )
        assert r.status_code == 201
        self.assertIn(b"success", r.data)

    def test_invalid_json_put(self):
        r = client.put(
            "/books/0-316-92004-5",
            content_type="application/json",
            data=json.dumps({"title": "Infinite Jest"}),
        )
        self.assertIn(b"error", r.data)

    def test_invalid_response(self):
        r = client.put(
            "/books/bad",
            content_type="application/json",
            data=json.dumps(
                {
                    "title": "The Hitchhiker's Guide to the Galaxy",
                    "author": "Douglas  Adams",
                }
            ),
        )
        assert r.status_code == 500

    def test_no_params_get(self):
        r = client.get("/health",)
        self.assertIn(b"OK", r.data)
        assert r.status_code == 200

    def test_no_params_post(self):
        r = client.post("/health",)
        self.assertIn(b"OK", r.data)
        assert r.status_code == 200

    def test_no_response_schema(self):
        r = client.get("/no-response-schema",)
        self.assertIn(b"response schemas", r.data)
        assert r.status_code == 500

    def test_no_response_schema_no_raise(self):
        r = client.get("/no-response-schema-no-raise",)
        assert r.status_code == 200

    def test_no_default_response_schema(self):
        r = client.get("/no-default-response-schema",)
        self.assertIn(b"Cannot locate response", r.data)
        assert r.status_code == 500

    def test_emit_all(self):
        with self.assertLogs(level="ERROR") as log:
            with pytest.warns(UserWarning):
                r = client.get("/emit-all",)
            assert "Validation of response failed" in log.output[0]
        # exception is handled @app.errorhandler(ValidationResponseError) so we assert its 500
        assert r.status_code == 500

    def test_valid_get(self):
        r = client.get(
            "/books/by-title",
            query_string={"title": "The Hitchhiker's Guide to the Galaxy"},
        )
        assert r.status_code == 200

    def test_valid_get_numeric_string(self):
        r = client.get("/books/by-title", query_string={"title": "1234"})
        assert r.status_code == 200

    def test_no_param_get(self):
        r = client.get("/books/by-author")
        self.assertIn(b"success", r.data)
        assert r.status_code == 200

    def test_path_param_invalid(self):
        r = client.get("/books/id/not-a-uuid", query_string={"title": "1234"})
        self.assertIn(b"error", r.data)

    def test_path_param_valid(self):
        r = client.get("/books/id/{}".format(uuid4()), query_string={"title": "1234"})
        self.assertIn(b"success", r.data)

    def test_mixed_required_params(self):
        r = client.get(
            "/books/by-author/{}".format("bob"), query_string={"title": "1234"}
        )
        self.assertIn(b"success", r.data)
