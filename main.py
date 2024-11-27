from fastapi import FastAPI
from contextlib import asynccontextmanager
from nats.aio.client import Client as NATS
from dotenv import load_dotenv
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from listeners.ItinerarieListener import message_handler

load_dotenv()

NATS_SERVER = os.getenv("NATS_SERVER")

nats_client = NATS()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código para inicializar la aplicación (equivalente a 'startup')
    await nats_client.connect(NATS_SERVER)
    asyncio.create_task(consume())
    
    # Devolver el control para iniciar la aplicación FastAPI
    yield
    
    # Código para cerrar la aplicación (equivalente a 'shutdown')
    await nats_client.drain()

# Inicializar la aplicación FastAPI con el manejador de ciclo de vida
app = FastAPI(lifespan=lifespan)

async def consume():
    try:
        await nats_client.connect(NATS_SERVER)
        await nats_client.subscribe("generate-plan", cb=message_handler)
        await nats_client.subscribe("get-itineraries", cb=message_handler)
        await nats_client.subscribe("create-itinerary", cb=message_handler)
        print("Escuchando mensajes...")
    except Exception as e:
        print(f"Error al conectar con NATS: {str(e)}")
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume())
    loop.run_forever()