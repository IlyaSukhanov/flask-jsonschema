import os
import unittest

from flask import Flask
from flask_oasschema import OASSchema, validate_request

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["OAS_FILE"] = os.path.join(app.root_path, "schemas", "oas_prefix.json")
jsonschema = OASSchema(app)


@app.route("/v1/health", methods=["GET"])
@validate_request()
def book_get_health():
    return "OK"


client = app.test_client()


class JsonSchemaPrefixTests(unittest.TestCase):
    def test_get_prefix(self):
        r = client.get("/v1/health",)
        self.assertIn(b"OK", r.data)
