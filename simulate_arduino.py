import requests
import time
import random

API_URL = "http://127.0.0.1:8000/readings/"
SENSOR_ID = 1 
ARDUINO_KEY = "mi_clave_secreta_de_la_mina"

print(f"Iniciando simulación con seguridad (ID: {SENSOR_ID})...")

def send_data(valor):
    payload = {
        "value": valor,
        "sensor_id": SENSOR_ID
    }
    
    headers = {
        "x-arduino-key": ARDUINO_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Enviado: {valor:.2f} | ID Lectura: {response.json().get('id')}")
        elif response.status_code == 403:
            print("Error 403: La clave secreta no coincide.")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")

valor_actual = 28
for i in range(10):
    valor_actual -= random.uniform(0.1, 2.0)
    send_data(valor_actual)
    time.sleep(1)

print("\nSimulación terminada.")