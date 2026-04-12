SHELL := /bin/bash
MISE := mise exec --
%:
	@echo ''
	@echo '>>> Running /lib:$@...'
	@$(MISE) $(MAKE) -C lib $@
	@echo ''
	@echo '>>> Running /examples:$@...'
	@STAGE=dev $(MISE) $(MAKE) -C examples $@

publish:
	@$(MISE) $(MAKE) -C lib publish

setup:
	mise install
