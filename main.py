import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from server.routes.default import router as default_router
from server.routes.langgraph import router as langgraph_router
from server.routes.qdrant import router as qdrant_router


load_dotenv()

app = FastAPI(title="CS-Chatbot API")
app.include_router(langgraph_router)
app.include_router(qdrant_router)
app.include_router(default_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


