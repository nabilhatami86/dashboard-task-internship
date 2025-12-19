from fastapi import FastAPI

app = FastAPI(
    title="ASMI Dashboard API",
    version="0.1.0"
)

@app.get("/")
def health_check():
    return {"status": "ok"}


