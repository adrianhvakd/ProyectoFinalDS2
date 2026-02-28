import requests
import time
import random

# Configuración
API_URL = "http://127.0.0.1:8000/readings/"
SENSOR_ID = 2  # Asegúrate de que este ID exista en tu tabla 'sensor'
ARDUINO_KEY = "mi_clave_secreta_de_la_mina" # Debe coincidir con tu router

print(f"🚀 Iniciando simulación con seguridad (ID: {SENSOR_ID})...")

def send_data(valor):
    payload = {
        "value": valor,
        "sensor_id": SENSOR_ID
    }
    
    # Definimos el header que tu FastAPI está esperando
    headers = {
        "x-arduino-key": ARDUINO_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Enviado: {valor:.2f} | ID Lectura: {response.json().get('id')}")
        elif response.status_code == 403:
            print("❌ Error 403: La clave secreta no coincide.")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"🔥 Error de conexión: {e}")

# Simulamos datos
valor_actual = 42.8
for i in range(15):
    valor_actual += random.uniform(0.1, 2.0)
    send_data(valor_actual)
    time.sleep(1)

print("\n🏁 Simulación terminada.")