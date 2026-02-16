.PHONY: install dev up up-d db-up down migrate migrate-create help stack stack-down

# Full-stack Docker targets (root docker-compose.yml)
stack:
	docker compose up --build

stack-down:
	docker compose down

# Delegate everything else to backend Makefile
%:
	$(MAKE) -C backend $@ msg="$(msg)"
