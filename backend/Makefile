.PHONY: install dev db-up db-down migrate migrate-create help

SHELL := /bin/bash

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies into current environment
	pip install -e .

dev: ## Run dev server with hot reload
	uvicorn app.main:app --reload

up: ## Start all services (db + api) with hot reload
	docker-compose up

up-d: ## Start all services in the background
	docker-compose up -d

db-up: ## Start only the database
	docker-compose up -d db

down: ## Stop all services
	docker-compose down

migrate: ## Apply all pending migrations
	alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	alembic revision --autogenerate -m "$(msg)"
