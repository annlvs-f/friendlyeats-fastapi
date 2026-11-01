from fastapi import FastAPI

from app.api.v1.restaurants import router as restaurants_router

app = FastAPI(title="FriendlyEats FastAPI")
app.include_router(restaurants_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}