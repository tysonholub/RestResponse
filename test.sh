#!/bin/bash

set -e
pipenv run flake8
pipenv run python -m pytest
