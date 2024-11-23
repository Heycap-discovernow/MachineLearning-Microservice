from fastapi import FastAPI
from controllers.ItinerarieController import itinerary_router

app = FastAPI()

app.include_router(itinerary_router, prefix="/itineraries")