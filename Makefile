clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style
	flake8 flask_oasschema tests
	black --check flask_oasschema/ tests/ setup.py

fmt: ## Fix style errors
	black flask_oasschema/ tests/ setup.py

test:
	py.test tests --cov=flask_oasschema --cov-report term-missing --cov-fail-under=100 --cov-branch

test-all: lint test

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*

install: clean
	pip install . --upgrade

install-dev: clean
	pip install -e '.[testing]' --upgrade

install-dep: clean
	pip install '.[deploy]'

