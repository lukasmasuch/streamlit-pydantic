.PHONY: all install check test docs build format release

all: help

install:
	python -m pip install pipenv
	pipenv --rm || true
	pipenv install --dev --skip-lock

check:
	# Run all formatting and linting checks:
	pipenv run black --check src
	pipenv run black --check tests
	pipenv run isort --profile black --check-only src
	pipenv run isort --profile black --check-only tests
	pipenv run pydocstyle src
	pipenv run mypy src
	pipenv run flake8 --show-source --statistics src
	pipenv run flake8 --show-source --statistics tests
	# Checking package safety
	pipenv check

format:
	# Format code via black and imports via isort:
	pipenv run black src
	pipenv run black tests
	pipenv run isort --profile black src
	pipenv run isort --profile black tests

docs:
	pipenv run lazydocs --overview-file=README.md --src-base-url=https://github.com/lukasmasuch/streamlit-pydantic/blob/main streamlit_pydantic

build: docs
	# Build distribution
	rm -rf ./dist
	rm -rf ./build
	pipenv run python -m build
	pipenv run twine check dist/*

test:
	pipenv run coverage erase
	pipenv run pytest -m "not slow"

release: build
	twine upload dist/*

help:
	@echo '----'
	@echo 'install             - install everything needed for development'
	@echo 'format              - run code formatters'
	@echo 'check               - run all formatting and linting checks'
	@echo 'test                - run unit tests'
	@echo 'docs                - build the documentation'
	@echo 'build               - build everything for release'
	@echo 'release             - upload the distribution to PyPI'

