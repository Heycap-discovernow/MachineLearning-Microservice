# main.py
from fastapi import FastAPI
from routes.routes import router as itineraries_router
from routes.mineria import router as mineria_router

app = FastAPI()

# Incluye los routers
app.include_router(itineraries_router, prefix="/itineraries")
app.include_router(mineria_router, prefix="/ml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
