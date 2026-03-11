"""List public GitHub gists for a given user."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path, Query
import httpx

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Shared HTTP client for connection pooling."""
    app.state.http = httpx.AsyncClient(base_url="https://api.github.com", headers={
        "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
    }, timeout=10.0, )
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "App is running.."}


@app.get("/{user}")
async def get_gists_for_user(user: str = Path(pattern=r"^[a-zA-Z0-9\-\_]+$"),
        page: int = Query(default=1, ge=1, description="Page number"),
        per_page: int = Query(default=30, ge=1, le=100, description="Results per page (max 100)"), ):
    """Fetch public gists with pagination. Forwards GitHub's status code on errors."""
    try:
        response = await app.state.http.get(f"/users/{user}/gists", params={"page": page, "per_page": per_page}, )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.HTTPError as exc:
        logger.error(f"GitHub API request failed for user={user}: {exc}")
        raise HTTPException(status_code=502, detail="Failed to reach GitHub API")

    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("gist_api.main:app", host="127.0.0.1", port=8080, reload=True)
