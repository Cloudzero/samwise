# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

.PHONY: help clean clean-pyc clean-build sdist

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean - clean-{build,pyc}"
	@echo "sdist - package"


clean: clean-build clean-pyc clean-analysis


clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-analysis:
	rm -fr coverage-reports/
	rm -fr test-results/
	rm -fr .scannerwork/
	rm -fr *_flake8.out

clean-pyc:
	find . -type f -name '*.py[co]' -exec rm -rf {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +


# Only run init if requirements-dev.txt is newer than SITE_PACKAGES location
.PHONY: init
SITE_PACKAGES := $(shell pip show pip | grep '^Location' | cut -f2 -d':')
init: $(SITE_PACKAGES)

$(SITE_PACKAGES): requirements-dev.txt             ## ensures all dev dependencies into the current virtualenv
	@if [[ "$$VIRTUAL_ENV" = "" ]] ; then printf "$(WARN_COLOR)WARN:$(NO_COLOR) No virtualenv found, install dependencies globally." ; fi
	pip install -r requirements-dev.txt


sdist: clean
	python setup.py sdist
	ls -l dist


bdist: clean
	python setup.py bdist_wheel

