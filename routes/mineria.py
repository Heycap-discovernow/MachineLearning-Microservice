from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Union
from routes.database import get_db
from datetime import date
from pydantic import BaseModel
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"message": "¡Bienvenido a la API de FastAPI!"}

class VistaResponse(BaseModel):
    vistas: int
    fecha: date

class VistasResponse(BaseModel):
    historical_data: List[VistaResponse]
    predicted_rows: List[VistaResponse]
    
@router.get("/vistas/{place_id}", response_model=VistasResponse)
async def get_vistas_por_dia(place_id: str, db: AsyncSession = Depends(get_db)):
    # 1. Buscar el place_id en la tabla 'places'
    query = """
        SELECT place_id 
        FROM places 
        WHERE google_id = :google_id;
    """
    result = await db.execute(text(query), {"google_id": place_id})
    place = result.fetchone()
    
    if not place:
        raise HTTPException(status_code=404, detail="Error: place not found")
    
    # 2. Obtener el conteo de vistas por día
    query = """
    SELECT 
        COUNT(*) AS vistas, 
        DATE(created_at) AS fecha
    FROM views
    WHERE place_id = :place_id
    GROUP BY DATE(created_at)
    ORDER BY fecha;
    """
    result = await db.execute(text(query), {"place_id": place.place_id})
    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No hay datos de vistas para este lugar")

    # 3. Convertir los resultados a un DataFrame
    df = pd.DataFrame(rows, columns=["vistas", "fecha"])
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)
    
    # 4. Interpolación para manejar posibles días faltantes
    df = df.asfreq('D')  # Asegura que las fechas sean diarias
    df['vistas'] = df['vistas'].interpolate(method='time')
    
    # 5. Ajustar el modelo Holt-Winters
    model = ExponentialSmoothing(df['vistas'], trend='add', seasonal=None)
    fit = model.fit()
    
    # 6. Pronosticar para los próximos 3 días
    forecast = fit.forecast(steps=3)
    
    # 7. Convertir el pronóstico a un formato compatible con la respuesta
    predicted_rows = [{"vistas": int(v), "fecha": date} for date, v in forecast.items()]
    
    # 8. Combinar los datos históricos con el pronóstico
    historical_data = [{"vistas": row.vistas, "fecha": row.fecha} for row in rows]

    
    return {"historical_data": historical_data, "predicted_rows": predicted_rows}
