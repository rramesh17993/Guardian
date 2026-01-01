.PHONY: install test lint format clean docker-build

install:
	poetry install

test:
	poetry run pytest tests/

lint:
	poetry run flake8 src/ tests/
	poetry run black --check src/ tests/
	poetry run isort --check src/ tests/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

docker-build:
	docker build -t guardian:latest .
