.PHONY: all build publish

all: build publish

build:
	python setup.py bdist_wheel --universal sdist

publish:
	twine upload dist/gixy-`grep -oP "(?<=version\s=\s['\"])[^'\"]*(?=['\"])" gixy/__init__.py`*

