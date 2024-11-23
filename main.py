# main.py
from fastapi import FastAPI
from routes.mineria import router as mineria_router
from controllers.ItinerarieController import itinerary_router

app = FastAPI()

# Incluye los routers
app.include_router(itinerary_router, prefix="/itineraries")
app.include_router(mineria_router, prefix="/ml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
