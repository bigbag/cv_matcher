.PHONY: help

#################################################################################
# GLOBALS                                                                        #
#################################################################################

# Project configuration
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = cv-matcher

# Path configuration
PROJECT_PATH = src
TESTS_PATH = tests
LINT_SOURCES_PATHS = ${PROJECT_PATH} ${TESTS_PATH}

# Environment configuration
CURRENT_PATH = $(shell pwd)
TEST_DIR = $(CURRENT_PATH)/${TESTS_PATH}

# Virtual environment configuration
VENV := $(or ${VIRTUAL_ENV},${VIRTUAL_ENV},.venv)
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UV = $(VENV)/bin/uv
PYCLEAN = $(VENV)/bin/pyclean
PYTEST = $(VENV)/bin/pytest

export UV_LINK_MODE=copy
export export PYTHONPATH=.

#################################################################################
# DEVELOPMENT ENVIRONMENT                                                        #
#################################################################################

## Create virtual environment
venv/create: 
	@echo "Creating virtual environment..."
	python -m venv $(VENV)
	@echo "Done"

## Install main dependencies
venv/install/main:
	@echo "Installing main dependencies..."
	$(PIP) install uv
	$(UV) sync

## Install all dependencies
venv/install/all:
	@echo "Installing all dependencies..."
	$(PIP) install uv 
	$(UV) sync --extra test


#################################################################################
# DATA MANAGEMENT                                                               #
#################################################################################

## Analyze resume and job description
analyze:
	@echo "Analyzing resume and job description..."
	$(PYTHON) ${PROJECT_PATH}/manage.py analyze --resume_path=$(RESUME_PATH) --job_desc_path=$(JOB_DESC_PATH)

## Start server
run/server:
	@echo "Running server"
	$(PYTHON) ${PROJECT_PATH}/manage.py start-server

#################################################################################
# DOCKER COMMANDS                                                               #
#################################################################################

## Build server docker image
docker/build/server:
	docker build -t cv-matcher-app -f ./Dockerfile .

## Run server docker image
docker/run/server:
	docker run --rm -it cv-matcher-app bash

#################################################################################
# QUALITY ASSURANCE                                                             #
#################################################################################

## Run all linters
lint: lint/black lint/flake8 lint/isort lint/bandit

lint/black:
	@echo "Linting using black..."
	$(PYTHON) -m black --check --diff $(LINT_SOURCES_PATHS)
	@echo "Done"

lint/flake8:
	@echo "Linting using flake8..."
	$(PYTHON) -m flake8 $(LINT_SOURCES_PATHS)
	@echo "Done"

lint/isort:
	@echo "Linting using isort..."
	$(PYTHON) -m isort --check-only --diff $(LINT_SOURCES_PATHS)
	@echo "Done"

lint/bandit:
	@echo "Linting using bandit..."
	$(PYTHON) -m bandit -r $(PROJECT_PATH)
	@echo "Done"

lint/mypy:
	@echo "Linting using mypy..."
	$(PYTHON) -m mypy --show-error-codes --skip-cache-mtime-checks $(LINT_SOURCES_PATHS)
	@echo "Done"

lint/yamllint:
	@echo "Linting YAML files"
	docker run --rm -v ${PWD}:/check/ -w /check/ pipelinecomponents/yamllint yamllint -f parsable -c /check/.yamllint .

## Format source code
format:
	@echo "Formatting code..."
	$(PYTHON) -m black $(LINT_SOURCES_PATHS)
	$(PYTHON) -m isort $(LINT_SOURCES_PATHS)
	@echo "Done"

## Run all tests
test:
	LOG_LEVEL=ERROR \
	PYTHONPATH=${PYTHONPATH} \
	$(UV) run \
	$(PYTEST) --disable-warnings $(TEST_DIR) $(PROJECT_PATH) -x -s --cov-report=term-missing --cov-config=setup.cfg --cov=src


## Clear temporary information
clean:  
	@echo "Clearing cache directories..."
	rm -rf .mypy_cache .pytest_cache .coverage
	$(PYCLEAN) .
	@rm -rf `find . -name __pycache__`
	@rm -rf `find . -type f -name '*.py[co]' `
	@rm -rf `find . -type f -name '*~' `
	@rm -rf `find . -type f -name '.*~' `
	@rm -rf `find . -type f -name '@*' `
	@rm -rf `find . -type f -name '#*#' `
	@rm -rf `find . -type f -name '*.orig' `
	@rm -rf `find . -type f -name '*.rej' `
	@rm -rf .coverage
	@rm -rf coverage.html
	@rm -rf coverage.xml
	@rm -rf htmlcov
	@rm -rf build
	@rm -rf cover
	@rm -rf .develop
	@rm -rf .flake
	@rm -rf .install-deps
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf dist
	@rm -rf test-reports

## Generate changelog file
sys/changelog:
	@echo "Generating CHANGELOG.md..."
	@echo "" > CHANGELOG.md;
	@previous_tag=0; \
	for current_tag in $$(git tag --sort=-creatordate); do \
		if [ "$$previous_tag" != 0 ]; then \
			tag_date=$$(git log -1 --pretty=format:'%ad' --date=short $${previous_tag}); \
			printf "\n## $${previous_tag} ($${tag_date})\n\n" >> CHANGELOG.md; \
			git log $${current_tag}...$${previous_tag} --pretty=format:'*  %s [%an]' --reverse | grep -v Merge >> CHANGELOG.md; \
			printf "\n" >> CHANGELOG.md; \
		fi; \
		previous_tag=$${current_tag}; \
	done
	@echo "CHANGELOG.md generated successfully."

## Create and push tag
sys/tag:
	@read -p "Enter tag version (e.g., 1.0.0): " TAG; \
	if [[ $$TAG =~ ^[0-9]+\.[0-9]+\.[0-9]+$$ ]]; then \
		git tag -a $$TAG -m $$TAG; \
		git push origin $$TAG; \
		echo "Tag $$TAG created and pushed successfully."; \
	else \
		echo "Invalid tag format. Please use X.Y.Z (e.g., 1.0.0)"; \
		exit 1; \
	fi

#################################################################################
# SELF-DOCUMENTING COMMANDS                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
