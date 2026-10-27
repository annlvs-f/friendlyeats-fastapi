from fastapi import FastAPI

app = FastAPI(title="FriendlyEats FastAPI")


@app.get("/health")
def health():
    return {"status": "ok"}