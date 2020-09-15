.PHONEY: setup
setup:
	pip install --force-reinstall -r requirements/requirements-dev.txt

.PHONY: lint
lint: lint-shell

.PHONY: lint-shell
lint-shell:
	shellcheck ./dev/*.sh

.PHONEY: test
test:
	pytest -v -s --cache-clear tests/

.PHONEY: safety
safety:
	bash ./dev/safety.sh