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

render-diagrams:
	./utilities/render_diagram.sh

generate-bot-session:
	poetry run python utilities/generate_session.py --bot

generate-client-session:
	poetry run python utilities/generate_session.py --client
