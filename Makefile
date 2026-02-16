.PHONY: install dev up up-d db-up down migrate migrate-create help

%:
	$(MAKE) -C backend $@ msg="$(msg)"
