from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.database import sessionmanager
from src.routers import content_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title="Content System")
app.include_router(content_router.router)


@app.get("/health-check", tags=["health check"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
