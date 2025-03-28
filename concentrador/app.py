from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from datetime import datetime
import os
from zoneinfo import ZoneInfo  # Para manejar la zona horaria de Madrid
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Medida(Base):
    __tablename__ = "medidas"
    id = Column(Integer, primary_key=True, index=True)
    generator_id = Column(String, index=True)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    rotor_speed = Column(Float)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Se almacena en UTC

# Crea la tabla en la base de datos si no existe
Base.metadata.create_all(bind=engine)

# Modelo Pydantic con validación: solo se aceptan valores correctos
class MedidaData(BaseModel):
    generator_id: str
    wind_speed: float = Field(..., gt=0)
    wind_direction: float = Field(..., ge=0, le=360)
    rotor_speed: float = Field(..., gt=0)
    temperature: float = Field(..., ge=-10, le=40)
    timestamp: datetime

API_KEY = os.getenv("API_KEY")
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI(dependencies=[Depends(verify_api_key)])

@app.post("/medidas")
def recibir_medida(medida: MedidaData):
    db = SessionLocal()
    try:
        db_medida = Medida(**medida.dict())
        db.add(db_medida)
        db.commit()
        return {"status": "success", "data": medida}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar los datos: {str(e)}")
    finally:
        db.close()

@app.get("/agregados/minuto")
def get_agregados_minuto():
    """
    Devuelve los agregados por minuto para cada métrica:
      - Promedio
      - Máximo (con el generador que lo produjo)
      - Mínimo (con el generador que lo produjo)

    Los resultados se ordenan de más reciente a más antiguo y el timestamp se convierte a la hora de Madrid.
    """
    db = SessionLocal()
    try:
        # Se obtiene cada minuto (agrupado) y se ordena de forma descendente
        minutes = db.query(func.date_trunc('minute', Medida.timestamp).label("minute"))\
                    .group_by(text("minute"))\
                    .order_by(text("minute DESC"))\
                    .all()
        metrics = ['wind_speed', 'wind_direction', 'rotor_speed', 'temperature']
        results = []
        for m in minutes:
            # Convertir el minuto a la zona horaria de Madrid
            minute_madrid = m.minute.astimezone(ZoneInfo("Europe/Madrid")).isoformat()
            data = {"minute": minute_madrid}
            for metric in metrics:
                avg_value = db.query(func.avg(getattr(Medida, metric)))\
                              .filter(func.date_trunc('minute', Medida.timestamp) == m.minute)\
                              .scalar()
                max_row = db.query(Medida.generator_id, getattr(Medida, metric))\
                            .filter(func.date_trunc('minute', Medida.timestamp) == m.minute)\
                            .order_by(getattr(Medida, metric).desc())\
                            .first()
                min_row = db.query(Medida.generator_id, getattr(Medida, metric))\
                            .filter(func.date_trunc('minute', Medida.timestamp) == m.minute)\
                            .order_by(getattr(Medida, metric).asc())\
                            .first()
                data[metric] = {
                    "avg": float(avg_value) if avg_value is not None else None,
                    "max": {"value": float(max_row[1]), "generator": max_row[0]} if max_row else None,
                    "min": {"value": float(min_row[1]), "generator": min_row[0]} if min_row else None
                }
            results.append(data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener agregados: {str(e)}")
    finally:
        db.close()

@app.get("/generadores")
def list_generators():
    db = SessionLocal()
    try:
        generators = db.query(Medida.generator_id).distinct().all()
        return {"generators": [g[0] for g in generators]}
    finally:
        db.close()

@app.get("/generadores/{generator_id}")
def get_generator_data(generator_id: str):
    db = SessionLocal()
    try:
        # Se ordenan los datos del generador de más reciente a más antiguo
        medidas = db.query(Medida)\
                     .filter(Medida.generator_id == generator_id)\
                     .order_by(Medida.timestamp.desc())\
                     .all()
        if not medidas:
            raise HTTPException(status_code=404, detail="Generador no encontrado")
        madrid_tz = ZoneInfo("Europe/Madrid")
        return {
            "generator_id": generator_id,
            "data": [
                {
                    "id": m.id,
                    "wind_speed": m.wind_speed,
                    "wind_direction": m.wind_direction,
                    "rotor_speed": m.rotor_speed,
                    "temperature": m.temperature,
                    # Convertir el timestamp a la hora de Madrid
                    "timestamp": m.timestamp.astimezone(madrid_tz).isoformat()
                } for m in medidas
            ]
        }
    finally:
        db.close()