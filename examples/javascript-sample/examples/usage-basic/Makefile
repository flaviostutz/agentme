SHELL := /bin/bash
MISE := mise exec --

.PHONY: install run clean

install:
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: $@"
	$(MISE) pnpm install

run:
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: $@"
	$(MISE) node index.js

clean:
	@echo ">>> ./examples/javascript-sample/examples/usage-basic: $@"
	rm -rf node_modules