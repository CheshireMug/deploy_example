start:
	uv run flask --app example run --port 8000

test-start:
	uv run flask --app example2 run --port 8000

debug-start:
	uv run flask --app example --debug run --port 8000
