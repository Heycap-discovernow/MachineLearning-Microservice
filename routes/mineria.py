from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Union
from routes.database import get_db
from datetime import date
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet

router = APIRouter()

@router.get("/")
async def hello_world():
    return {"message": "¡Bienvenido a la API de FastAPI!"}

class VistaResponse(BaseModel):
    vistas: int
    fecha: date

@router.get("/vistas/{place_id}", response_model=List[VistaResponse])
async def get_vistas_por_dia(place_id: str, db: AsyncSession = Depends(get_db)):
  
  query = """
    SELECT place_id 
    FROM places 
    WHERE google_id = :google_id;
    """
  result = await db.execute(text(query), {"google_id": place_id})
  place = result.fetchone()
  
  if not place:
    raise HTTPException(status_code=404, detail="Error: place not found")
    
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
  
  '''
  {
        "vistas": 21,
        "fecha": "2024-11-10"
    },
    {
        "vistas": 9,
        "fecha": "2024-11-11"
    },
  '''
  df = pd.DataFrame(rows)
  df.info()
  df['fecha'] = pd.to_datetime(df['fecha'])
  df.set_index('fecha', inplace=True)
  
  df_prophet = df.interpolate(method='time').copy()
  df_prophet.reset_index(inplace=True)
  df_prophet.rename(columns={'fecha': 'ds', 'vistas': 'y'}, inplace=True)

  model = Prophet(daily_seasonality=True)
  model.fit(df_prophet)
  future = model.make_future_dataframe(periods=3)
  forecast = model.predict(future)
  predicted_data = forecast[forecast['ds'] > df_prophet['ds'].max()]
   
  # for _, row in predicted_data.iterrows():
  #   rows.append({"vistas": int(row['yhat']), "fecha": row['ds'].date()})
  
  return [{"vistas": row.vistas, "fecha": row.fecha} for row in rows]
