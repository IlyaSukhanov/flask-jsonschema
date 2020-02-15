# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import parse_qsl, urlparse

import jsonref
from flask import current_app, request
from jsonschema import validate


UUID_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class OASSchema(object):
    def __init__(self, app):
        self.app = app
        self._state = self.init_app(app)

    def init_app(self, app):
        default_file = os.path.join(app.root_path, "schemas", "oas.json")
        schema_path = app.config.get("OAS_FILE", default_file)
        with open(schema_path, "r") as schema_file:
            schema = jsonref.load(schema_file)
        app.extensions["oas_schema"] = schema
        return schema

    def __getattr__(self, name):
        return getattr(self._state, name, None)


def schema_property(parameter_definition):
    schema_keys = ["type", "format", "enum", "pattern"]
    properties = {
        key: parameter_definition[key]
        for key in parameter_definition
        if key in schema_keys
    }

    # stoplight supports a uuid format which is not json schema
    if properties.get("format") == "uuid":
        del properties["format"]
        properties["pattern"] = UUID_REGEX

    return properties


def extract_body_schema(path_schema, method):

    method_parameters = path_schema[method].get("parameters", {})
    for parameter in method_parameters:
        if parameter.get("in", "") == "body":
            return parameter["schema"]

    return {}


def extract_param_schema(param, parameters):

    schema_parameters = [
        schema_param
        for schema_param in parameters
        if schema_param.get("in", "") == param
    ]
    schema = {
        "type": "object",
        "properties": {
            parameter["name"]: schema_property(parameter)
            for parameter in schema_parameters
        },
        "required": [
            parameter["name"]
            for parameter in schema_parameters
            if parameter.get("required", False)
        ],
    }

    if len(schema["required"]) == 0:
        del schema["required"]

    return schema


def extract_path_schema(request, schema):
    schema_prefix = schema.get("basePath")

    uri_path = request.url_rule.rule.replace("<", "{").replace(">", "}")
    if schema_prefix and uri_path.startswith(schema_prefix):
        uri_path = uri_path[len(schema_prefix) :]

    return schema["paths"][uri_path]


def query_string_as_dict(uri):
    return dict(parse_qsl(urlparse(request.url).query))


def validate_request():
    """
    Validate request against JSON schema in OpenAPI Specification

    Args:
        path      (string): OAS style application path http://goo.gl/2FHaAw
        method    (string): OAS style method (get/post..) http://goo.gl/P7LNCE

    Example:
        @app.route("/foo/<param>/bar", methods=["POST"])
        @validate_request()
        def foo(param):
            ...
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            method = request.method.lower()
            schema = current_app.extensions["oas_schema"]
            path_schema = extract_path_schema(request, schema)

            # validate path parameters
            path_parameters = path_schema.get("parameters")
            if path_parameters is not None:
                validate(
                    request.view_args, extract_param_schema("path", path_parameters)
                )

            # validate query string params
            request_parameters = path_schema[method].get("parameters")
            if request_parameters:
                validate(
                    query_string_as_dict(request.url),
                    extract_param_schema("query", request_parameters),
                )

            # validate body
            if method in ("post", "put", "patch"):
                validate(request.get_json(), extract_body_schema(path_schema, method))

            return fn(*args, **kwargs)

        return decorated

    return wrapper
