from fastapi import FastAPI

from .routers import terms


app = FastAPI(title="Glossary Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(terms.router)