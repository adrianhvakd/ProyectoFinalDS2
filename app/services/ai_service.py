import pandas as pd
import numpy as np
from typing import List
from app.models.reading import Reading
from sklearn.linear_model import LinearRegression

def predict_sensor_failure(recent_readings: List[Reading]):

    if len(recent_readings) < 5:
        return {
            "status": "Iniciando", 
            "message": "Se necesitan al menos 5 lecturas para un análisis predictivo."
        }

    data = [r.value for r in recent_readings]
    df = pd.DataFrame(data, columns=['value'])
    
    X = np.array(range(len(df))).reshape(-1, 1)
    y = df['value'].values

    model = LinearRegression()
    model.fit(X, y)
    
    slope = model.coef_[0]
    
    volatility = df['value'].std()

    if slope > 0.5:
        prediction = "Riesgo de sobrepaso"
        message = "La tendencia indica que el valor superará el umbral pronto."
    elif volatility > (df['value'].mean() * 0.2):
        prediction = "Posible fallo de hardware"
        message = "Lecturas muy inestables detectadas; revisar conexión física del sensor."
    else:
        prediction = "Estable"
        message = "El comportamiento del sensor es normal."

    return {
        "prediction": prediction,
        "slope": round(float(slope), 4),
        "volatility": round(float(volatility), 4),
        "message": message
    }