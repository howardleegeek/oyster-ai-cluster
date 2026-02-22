from fastapi import FastAPI
from agent_sdk.api import router

app = FastAPI(
    title="Agent SDK",
    description="Modular, pluggable SDK for external task execution",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
