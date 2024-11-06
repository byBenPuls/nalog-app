.PHONY: all


SHELL=/bin/bash -e
VERSION := $(shell grep 'version =' pyproject.toml | cut -d '"' -f 2)
TARGET=$(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)
VENV_DIR := ./.venv

push:
	git push && git push --tags

format:
	poetry run ruff format .
	poetry run ruff check --fix .

test:
	poetry run pytest . -p no:logging -p no:warnings

setup:
	python3 run.py

build-app:
	@echo "Starting to build the app $(VERSION) for $(TARGET) $(ARCH)"

	poetry install --with dev
	poetry show
	pyinstaller --onefile \
	--name "nalog-$(VERSION)-$(TARGET)-$(ARCH)" \
	-i "./assets/wb.ico" \
	--noconsole \
	 run.py

os:
	@echo "$(TARGET) $(ARCH)"

update:
	poetry update

release:
	poetry version $(version)

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*.spec' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f report.html
	rm -f .coverage
	rm -rf {build,dist,site,.cache,.mypy_cache,.ruff_cache,reports}

check-dir:
	@if [ -d $(VENV_DIR) ]; then \
		echo "Directory '$(VENV_DIR)' exists."; \
	else \
		echo "Directory '$(VENV_DIR)' does not exist. Creating..."; \
		#mkdir -p $(VENV_DIR); \
	fi