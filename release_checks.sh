#!/bin/sh

echo -- Run pytest with coverage
pytest tests/ --doctest-modules --cov=ynca --cov-report=html


echo -- Run mypy type checks
mypy src/ynca --check-untyped-defs