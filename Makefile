generate-session:
	poetry run python utilities/generate_session.py

build:
	docker compose build

up-all:
	docker compose up --build

up-infra:
	docker compose up postgres migration --build
