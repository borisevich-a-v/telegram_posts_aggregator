generate-session:
	poetry run python utilities/generate_session.py

build:
	docker compose build

up-all:
	docker compose up --build

.PHONY: up-infra up-local

up-infra:
	docker compose up -d postgres migration --build

up-local: up-infra
	poetry install
	poetry run python -m aggregator

down:
	docker compose down

render_diagrams:
	./utilities/render_diagram.sh
