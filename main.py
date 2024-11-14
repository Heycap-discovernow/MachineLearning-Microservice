from fastapi import FastAPI
from routes import routes as router
import dtos.request.PlaceRequest as placeRequest

app = FastAPI()

app.include_router(router, prefix="/itineraries")