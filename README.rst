Flask-OASSchema
================

JSON request validation for Flask applications using a JSON Schema specified in a `OpenAPI Specification <https://github.com/OAI/OpenAPI-Specification>`_ (also know as OAS and Swagger).

Validating schema of passed object provides a level of confidence of correctness of data directly proportional to schema strictness. With a good schema, it maybe be possible to use JSON-dict like object as first order models without having to convert them into trusted python objects. Reducing amount of code that needs to be maintained.

Examples
--------

Basic request validation
~~~~~~~~~~~~~~~~~~~~~~~~

The `tests <test.py>`_ provide a succinct example of usage as well as an example `OAS schema file <schemas/oas.json>`_. But at high level usage looks as follows::

    from flask import Flask
    from flask_oasschema import OASSchema, validate_request, ValidationError

    # Configure application
    app = Flask(__name__)

    # Specify path to the OAS schema file, in this case schemas/oas.json of
    # project firectory
    app.config['OAS_FILE'] = os.path.join(
        app.root_path,
        'schemas',
        'oas.json'
    )

    # Initialize validator
    jsonschema = OASSchema(app)


    # Define default behavior for request validation error
    @app.errorhandler(ValidationError)
    def on_request_error(e):
        return f"error {e}", 400


    # Decorate endpoint with @validate_request()
    @app.route('/books/<isbn>', methods=['POST'])
    @validate_request()
    def books(isbn):
        return 'success'


Response validation
~~~~~~~~~~~~~~~~~~~

While with request validation its rather intuitive what to do when request does not conform with schema, respond with a 400. With responses things are a bit tricky, depending on user preference Flask-OASSchema can be configured to log, warn, or raise an exception.


Behavior of response validation can be configured by endpoint::

    ...
    # Decorate endpoint with @validate_request()
    @app.route('/books/<isbn>', methods=['POST'])
    @validate_response(emit_exception=True, emit_warning=False, emit_log=False)
    def books(isbn):
        return 'success'
    ...

Or globally::

    ...
    # Initialize validator
    jsonschema = OASSchema(app, response_emit_exception=False, reponse_emit_warning=False, response=emit_log=True)

When using Exception emission a error handler can be setup to return specific payload to client::

    ...
    from flask_oasschema import ValidationResponseError
    ...
    @app.errorhandler(ValidationResponseError)
    def on_response_error(e):
        return f"error {e}", 500
    ...


Installation
------------

This library is available through `PyPI <https://pypi.python.org/pypi>`_ as `Flask-OASSchema <https://pypi.python.org/pypi/Flask-OASSchema/0.9.1>`_ and as such can be installed with::

    pip install Flask-OASSchema


Credit
------

This project is a fork of `Matt Wright's <https://github.com/mattupstate>`_ project `Flask-JsonSchema <https://github.com/mattupstate/flask-jsonschema>`_ and thus borrows ideas and code. Difference being that Flask-OASSchema works only with OAS (Swagger) style schema spec as opposed to raw json-schema. This allows Flask-OASSchema to locate schema corresponding to endpoint and method without explicit per endpoint configuration.

Authors:
`Dan Baumann <https://github.com/dbaumann>`_
`Thanavath Jaroenvanit <https://github.com/Thanavath>`_
