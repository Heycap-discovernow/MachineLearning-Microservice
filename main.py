from fastapi import FastAPI
from routes import routes as router
from routes import mineria as mineria
import dtos.request.PlaceRequest as placeRequest

app = FastAPI()

app.include_router(router, prefix="/itineraries")
app.include_router(mineria, prefix="/ml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    