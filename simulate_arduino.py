import requests
import time
import random

API_URL = "http://127.0.0.1:8000/readings/"

# API keys de tus sensores (obténolas de Supabase: SELECT api_key FROM sensor)
API_KEY_GAS = "eb8aef05-776d-41c0-a48b-65fef389a440"
API_KEY_TEMP = "2e8812a1-db26-4b6a-a354-da811c93ffbe"

def send_reading(api_key, value):
    payload = {"value": value}
    headers = {"x-arduino-key": api_key}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Enviado: {value:.2f} | ID: {response.json().get('id')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")

# Valores iniciales
gas_value = 8.7
temp_value = 25.6

print("Iniciando simulación... (Ctrl+C para detener)")

while True:
    # Variación aleatoria
    gas_value -= random.uniform(-1, 2)
    temp_value -= random.uniform(-1, 1)
    
    # Mantener en rango
    gas_value = max(0, min(5, gas_value))
    temp_value = max(15, min(45, temp_value))
    
    # Enviar a ambos sensores
    send_reading(API_KEY_GAS, gas_value)
    send_reading(API_KEY_TEMP, temp_value)
    
    time.sleep(5)
