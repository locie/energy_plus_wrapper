.PHONY: clean-pyc clean-build

clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive .eggs/
	rm --force --recursive .cache/
	rm --force --recursive .tox/
	rm --force --recursive *.egg-info
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.coverage' -exec rm -f {} \;
	find . -type d -name "__pycache__" -delete
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' ! -name '*.un~' -exec rm -f {} \;

env:
	pip install -Ur requirements.txt
	pip install .

init:
	pip install coveralls
	pip install isort
	pip install pytest-cov
	pip install pytest-pep8
	pip install nbsphinx
	pip install pylama
	pip install twine
	pip install recommonmark

test:
	pytest

lint:
	pylama

isort:
	sh -c "isort --recursive . "

build: clean
	python setup.py check
	python setup.py sdist
	twine upload dist/*

doc:
	$(MAKE) -C source_doc notebooks
	$(MAKE) -C source_doc epub
	$(MAKE) -C source_doc latexpdf
	sphinx-build -b html source_doc/source docs
