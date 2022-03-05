# Automation of various common tasks

# Format all source code
.PHONY: format
format:
	black src/
	black test/

# Lint all source code
.PHONY: lint
lint:
	flake8 src/
	flake8 test/

# Typecheck all source code
.PHONY: typecheck
typecheck:
	mypy src/
	mypy test/

# Run unit tests with tox
.PHONY: test
test:
	tox
