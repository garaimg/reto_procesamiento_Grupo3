import os
import time
import requests
import random
import socket
from datetime import datetime

API_KEY = os.getenv("API_KEY", "secret123")
CONCENTRADOR_URL = os.getenv("CONCENTRADOR_URL", "http://concentrador:8000/medidas")
# Usa el hostname del contenedor para el identificador
GENERATOR_ID = f"GEN-{socket.gethostname()}"

# Probabilidad de enviar datos erróneos (20%)
ERROR_PROBABILITY = 0.2


def generar_dato():
    # Valores correctos
    wind_speed = round(random.uniform(5, 25), 2)
    wind_direction = round(random.uniform(0, 360), 2)
    rotor_speed = round(random.uniform(500, 3000), 2)
    temperature = round(random.uniform(-5, 35), 2)

    # Con probabilidad ERROR_PROBABILITY, se introducen errores en cada métrica
    if random.random() < ERROR_PROBABILITY:
        wind_speed = round(random.uniform(-10, 0), 2)
    if random.random() < ERROR_PROBABILITY:
        wind_direction = round(random.uniform(361, 720), 2)
    if random.random() < ERROR_PROBABILITY:
        rotor_speed = round(random.uniform(-100, 0), 2)
    if random.random() < ERROR_PROBABILITY:
        temperature = round(random.uniform(50, 100), 2)

    return {
        "generator_id": GENERATOR_ID,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "rotor_speed": rotor_speed,
        "temperature": temperature,
        "timestamp": datetime.utcnow().isoformat()
    }


while True:
    try:
        data = generar_dato()
        response = requests.post(
            CONCENTRADOR_URL, json=data,
            headers={"x-api-key": API_KEY}
        )
        print(f"[{GENERATOR_ID}] Enviado: {data} | Respuesta: {response.status_code}")
    except Exception as e:
        print(f"[{GENERATOR_ID}] Error enviando datos: {e}")
    time.sleep(random.uniform(1, 5))
