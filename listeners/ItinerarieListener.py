from typing import List
from pydantic import BaseModel
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from services.genetic_algorithm.run import ag_service
from repositories.ItineraryRepository import save_itinerary, get_itineraries, serialize_doc

class PlaceRequest(BaseModel):
    name: str
    lat: str
    lon: str
    time: str | None = None
    cost: str
    
class PlanRequest(BaseModel):
    hours: str
    quote: str
    places: List[PlaceRequest]

class SegmentRoute(BaseModel):
    origin_name: str
    origin_coord: tuple
    time_visit: int
    cost_visit: float
    target_name: str
    target_coord: tuple
    transport: str
    
class ItinerarieRequest(BaseModel):
    user_uuid: str
    route: List[SegmentRoute]
    polyline: str
    total_cost: float
    total_time: str

# Manejo de eventos de NATS
async def message_handler(msg):
    subject = msg.subject
    data = msg.data.decode()
    print(f"Recibido un mensaje en {subject}: {data}")
    
    try:
        message_data = json.loads(data)
        # Deserializar los datos recibidos
        if subject == "generate-plan":
            plan_request = PlanRequest(**message_data["data"])
            result = await generate_plan(plan_request)
            await msg.respond(json.dumps(result).encode())

        elif subject == "get-itineraries":
            user_uuid = message_data["data"]
            result = await itinieraries_history(user_uuid)
            # print("Result: ", result)
            await msg.respond(json.dumps(serialize_doc(result)).encode())

        elif subject == "create-itinerary":
            itinerary_request = ItinerarieRequest(**message_data["data"])
            result = await create_itinerarie(itinerary_request)
            await msg.respond(json.dumps(result).encode())

        else:
            print(f"El tema '{subject}' no está siendo escuchado.")
    
    except Exception as e:
        print(f"Error al procesar el mensaje en el tema '{subject}': {str(e)}")

async def generate_plan(createItinerary: PlanRequest):
    try:
        places_dict = [place.dict() for place in createItinerary.places]
        best_route = ag_service(places_dict, createItinerary.hours, createItinerary.quote)
        return {"message": best_route}
    except ValueError as e:
        return {"message": f"Error de valor: {str(e)}"}
    except Exception as e:
        return {"message": f"Error inesperado: {str(e)}"}
    
async def create_itinerarie(new_itinerary: ItinerarieRequest):
    try:
        result = await save_itinerary(new_itinerary)
        return {"message": "Itinerario creado exitosamente with uuid: " + result}
    except Exception as e:
        return {"message": str(e)}

async def itinieraries_history(user_uuid: str):
    try:
        result = await get_itineraries(user_uuid)
        return result
    except Exception as e:
        return {"message": str(e)}
        
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(consume())
#     loop.run_forever()