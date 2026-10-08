.PHONY: dev test build seed start clean

# Run backend and frontend in development mode
dev:
	uvicorn backend.main:app --reload --port 8000

# Run all backend and frontend test suites
test:
	python -m pytest tests/
	cd frontend && npm test

# Build production frontend assets
build:
	cd frontend && npm install && npm run build

# Seed SQLite database with demo patients
seed:
	python -m backend.seed

# Start production server serving both API and static SPA
start: build seed
	uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Clean temporary files and caches
clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]"
