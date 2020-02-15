# -*- coding: utf-8 -*-
"""
    flask_oasschema
    ~~~~~~~~~~~~~~~~

    flask_oasschema
"""
from future.standard_library import install_aliases
install_aliases()

import os
from functools import wraps
from urllib.parse import parse_qsl, urlparse
import json

import jsonref
from flask import current_app, request
from jsonschema import ValidationError, validate


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
        for key in parameter_definition if key in schema_keys
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


def extract_query_schema(parameters):

    query_params = [param for param in parameters if param.get("in", "") == "query"]
    schema = {
        "type": "object",
        "properties": {
            parameter["name"]: schema_property(parameter)
            for parameter in query_params
        },
        "required": [
            parameter["name"]
            for parameter in query_params if parameter.get("required", False)
        ]
    }

    if len(schema["required"]) == 0:
        del schema["required"]

    return schema


def extract_path_param_schema(parameters):

    path_params = [param for param in parameters if param.get("in", "") == "path"]
    schema = {
        "type": "object",
        "properties": {
            parameter["name"]: schema_property(parameter)
            for parameter in path_params
        },
        "required": [
            parameter["name"]
            for parameter in path_params if parameter.get("required", False)
        ]
    }

    if len(schema["required"]) == 0:
        del schema["required"]

    return schema


def extract_path_schema(request, schema):
        schema_prefix = schema.get("basePath")

        uri_path = request.url_rule.rule.replace("<", "{").replace(">", "}")
        if schema_prefix and uri_path.startswith(schema_prefix):
            uri_path = uri_path[len(schema_prefix):]

        return schema["paths"][uri_path]


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
                path_param_schema = extract_path_param_schema(path_parameters)
                validate(request.view_args, path_param_schema)

            # validate query string params
            parsed_url = urlparse(request.url)
            query = dict(parse_qsl(parsed_url.query))

            request_parameters = path_schema[method].get("parameters")
            if request_parameters:
                query_schema = extract_query_schema(request_parameters)
                validate(query, query_schema)

            if method in ("post", "put", "patch"):
                validate(request.get_json(), extract_body_schema(path_schema, method))

            return fn(*args, **kwargs)
        return decorated
    return wrapper
