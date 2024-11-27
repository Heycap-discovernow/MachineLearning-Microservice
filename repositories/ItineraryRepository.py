from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Conectar con MongoDB usando motor (asíncrono)
client = AsyncIOMotorClient(DATABASE_URL)

# Obtener la base de datos
db = client.get_database('discovernow')  # Nombre de la base de datos

# Obtener la colección
collection = db.get_collection('itineraries')  # Nombre de la colección

async def save_itinerary(request):
    itinerary_request = request.dict()  # Obtener los datos del request

    # Datos a insertar
    itinerary = {
        'user_uuid': itinerary_request['user_uuid'],
        'route': itinerary_request['route'],
        'polyline': itinerary_request['polyline'],
        'total_time': itinerary_request['total_time'],
        'total_cost': itinerary_request['total_cost']
    }

    try:
        # Insertar el documento en la colección
        response = await collection.insert_one(itinerary)
        print("Documento insertado, ID:", response.inserted_id)
        return str(response.inserted_id)  # Retornar el ID del documento insertado
    except Exception as e:
        return str(e)

async def get_itineraries(user_uuid):
    try:
        # Buscar el itinerario por 'user_uuid'
        response = collection.find({'user_uuid': user_uuid})
        itineraries = await response.to_list(length=None)
        if itineraries:
            return serialize_doc(itineraries)  # Serializar los documentos encontrados
        else:
            print("No se encontró ningún itinerario para este user_uuid")
            return None  # Retorna None si no se encuentra ningún itinerario
    except Exception as e:
        return str(e)


def serialize_doc(doc):
    """
    Convierte un documento de MongoDB a un formato serializable en JSON.
    """
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc