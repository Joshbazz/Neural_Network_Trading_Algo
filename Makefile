# How to Use the Makefile
# To use the Makefile, you run the make command followed by the target name. For example:

# make requirements installs the required Python packages.
# make clean deletes compiled Python files.
# make lint checks the code style.
# make format formats the code.
# make create_environment sets up the Python environment.
# make data prepares the dataset.
# make help lists all available commands.


#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = neural_network_trading_algo
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
# requirements: Installs Python dependencies listed in requirements.txt.
# .PHONY indicates that requirements is not a file but a command.
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	



## Delete all compiled Python files
# clean: Deletes all compiled Python files (*.pyc and *.pyo) and __pycache__ directories.
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 neural_network_trading_algo
	isort --check --diff --profile black neural_network_trading_algo
	black --check --config pyproject.toml neural_network_trading_algo

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml neural_network_trading_algo




## Set up python interpreter environment
# create_environment: Creates a Conda environment for the project.
.PHONY: create_environment
create_environment:
	
	conda create --name $(PROJECT_NAME) python=$(PYTHON_VERSION) -y
	
	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make Dataset
# data: Runs the make_dataset.py script to prepare the dataset, ensuring dependencies are installed first.
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) neural_network_trading_algo/data/make_dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################
# This section makes the Makefile self-documenting, providing a help command that lists available rules.

# help: When you run make help, this target prints out a list of all available commands with their descriptions.
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
