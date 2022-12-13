#!/bin/sh

echo -- Run pytest with coverage
pytest --cov=ynca tests/ --cov-report term-missing --cov-report html

echo -- Run mypy type checks
mypy ynca --check-untyped-defs