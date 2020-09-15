.PHONEY: setup
setup:
	pip install --force-reinstall -r requirements/requirements-dev.txt

.PHONY: lint
lint: lint-shell lint-python lint-docker

.PHONY: lint-shell
lint-shell:
	bash ./dev/lint_shell.sh

.PHONY: lint-python
lint-python:
	bash ./dev/lint_python.sh

.PHONY: lint-docker
lint-docker:
	bash ./dev/lint_dockerfiles.sh

.PHONEY: test
test:
	pytest -v -s --cache-clear tests/

.PHONEY: safety
safety:
	bash ./dev/safety.sh
