# list-gists

FastAPI service that lists public GitHub gists for any user.

## Run the API (~92 MB image size)

```bash
# Build the image
docker build -t list-gists:0.1.0 .
# Run the image as a container
docker run -d -p 8080:8080 --cap-drop=ALL --security-opt=no-new-privileges:true list-gists:0.1.0
```

## Usage

```bash
curl http://localhost:8080/octocat
curl "http://localhost:8080/octocat?page=1&per_page=2"
```

API docs: http://localhost:8080/docs


## Local Development Setup

```bash
uv sync
uv run uvicorn gist_api.main:app --host 127.0.0.1 --port 8080 --reload
```

## Tests

```bash
uv run pytest -v

# Or via Docker (no local UV/Python required)
docker run --rm -w /app -v "$PWD":/app ghcr.io/astral-sh/uv:python3.14-alpine uv run pytest -v
```

