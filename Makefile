.PHONEY: setup
setup:
	pip install --force-reinstall -r requirements/requirements-dev.txt

.PHONY: lint
lint: lint-shell

.PHONY: lint-shell
lint-shell:
	shellcheck ./dev/*.sh

.PHONY: lint-python
lint-python:
	pylint -v bigquery_lineage tests

.PHONY: lint-docker
lint-docker:
	bash ./dev/lint_dockerfiles.sh

.PHONEY: test
test:
	pytest -v -s --cache-clear tests/

.PHONEY: safety
safety:
	bash ./dev/safety.sh
