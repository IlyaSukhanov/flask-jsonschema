import os
import unittest
from uuid import uuid4

try:
    import simplejson as json
except ImportError:
    import json

from flask import Flask
from flask_oasschema import OASSchema, validate_request, ValidationError

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['OAS_FILE'] = os.path.join(app.root_path, 'schemas', 'oas.json')
jsonschema = OASSchema(app)


@app.route('/books/<isbn>', methods=['PUT'])
@validate_request()
def book_post(isbn):
    return 'success'


@app.route('/books/id/<book_uuid>', methods=['GET'])
@validate_request()
def book_get_by_id(book_uuid):
    return 'success'


@app.route('/books/by-author', methods=['GET'])
@validate_request()
def books_get_author():
    return 'success'


@app.route('/books/by-title', methods=['GET'])
@validate_request()
def books_get_title():
    return 'success'


@app.route('/books/by-author/<author>', methods=['GET'])
@validate_request()
def books_by_author_and_title_filter(author):
    return 'success'


@app.errorhandler(ValidationError)
def on_error(e):
    return 'error'

client = app.test_client()


class JsonSchemaTests(unittest.TestCase):

    def test_valid_json_put(self):
        r = client.put(
            '/books/0-330-25864-8',
            content_type='application/json',
            data=json.dumps({
                'title': 'The Hitchhiker\'s Guide to the Galaxy',
                'author': 'Douglas  Adams'
            })
        )
        self.assertIn(b'success', r.data)

    def test_invalid_json_put(self):
        r = client.put(
            '/books/0-316-92004-5',
            content_type='application/json',
            data=json.dumps({
                'title': 'Infinite Jest'
            })
        )
        self.assertIn(b'error', r.data)

    def test_valid_get(self):
        r = client.get(
            '/books/by-title',
            query_string={
                'title': 'The Hitchhiker\'s Guide to the Galaxy'
            }
        )
        self.assertIn(b'success', r.data)

    def test_valid_get_numeric_string(self):
        r = client.get(
            '/books/by-title',
            query_string={
                'title': '1234'
            }
        )
        self.assertIn(b'success', r.data)

    def test_no_param_get(self):
        r = client.get(
            '/books/by-author'
        )
        self.assertIn(b'success', r.data)

    def test_path_param_invalid(self):
        r = client.get(
            '/books/id/not-a-uuid',
            query_string={
                'title': '1234'
            }
        )
        self.assertIn(b'error', r.data)

    def test_path_param_valid(self):
        r = client.get(
            '/books/id/{}'.format(uuid4()),
            query_string={
                'title': '1234'
            }
        )
        self.assertIn(b'success', r.data)

    def test_mixed_required_params(self):
        r = client.get(
            '/books/by-author/{}'.format('bob'),
            query_string={
                'title': '1234'
            }
        )
        self.assertIn(b'success', r.data)
