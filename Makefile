
.PHONY: help
help:
	@# Magic line used to create self-documenting makefiles.
	@# See https://stackoverflow.com/a/35730928
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' Makefile | column -s: -t

.PHONY: all
# Install everything needed for development and run all checks.
all: install check

.PHONY: install
# Install everything needed for development.
install:
	python -m pip install pipenv
	pipenv --rm || true
	pipenv install --dev --skip-lock

.PHONY: check
# Run all formatting and linting checks.
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

.PHONY: format
# Run code formatters.
format:
	# Format code via black and imports via isort:
	pipenv run black src
	pipenv run black tests
	pipenv run isort --profile black src
	pipenv run isort --profile black tests

.PHONY: docs
# Build the API documentation.
docs:
	pipenv run lazydocs --overview-file=README.md --src-base-url=https://github.com/lukasmasuch/streamlit-pydantic/blob/main streamlit_pydantic

.PHONY: build
# Build everything for release.
build: docs
	rm -rf ./dist
	rm -rf ./build
	pipenv run python -m build
	pipenv run twine check dist/*

.PHONY: test
# Run unit tests.
test:
	pipenv run coverage erase
	pipenv run pytest -m "not slow"

.PHONY: release
# Build everything and upload distribution to PyPi.
release: build
	twine upload -u "__token__" dist/*
