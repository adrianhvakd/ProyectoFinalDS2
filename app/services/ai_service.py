"""
Sistema de Análisis Predictivo para Sensores Mineros
=====================================================

Este módulo proporciona análisis avanzado en tiempo real para sensores de gas y temperatura.
Detecta: Deriva, Ruido excesivo y Predicción de superación de umbrales.

Autor: Sistema de Monitoreo Minero
Versión: 2.0
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Análisis estadístico y ML
from sklearn.linear_model import LinearRegression, TheilSenRegressor
from scipy import stats


class SensorStatus(Enum):
    """Estados posibles del sensor"""
    ESTABLE = "Estable"
    ADVERTENCIA = "Advertencia"
    ALERTA = "Alerta"
    CRITICO = "Crítico"
    INICIANDO = "Iniciando"


class AlertType(Enum):
    """Tipos de alerta detectados"""
    OK = "OK"
    DERIVA_POSITIVA = "Deriva Positiva"
    DERIVA_NEGATIVA = "Deriva Negativa"
    RUIDO_EXCESIVO = "Ruido Excesivo"
    UMBRAL_MAX = "Superación Umbral Máximo"
    UMBRAL_MIN = "Superación Umbral Mínimo"
    PREDICCION_MAX = "Predicción Umbral Máximo"
    PREDICCION_MIN = "Predicción Umbral Mínimo"
    SENSOR_ATASCADO = "Sensor Atascado"
    SENSOR_DESCONECTADO = "Sensor Desconectado"


@dataclass
class AnalysisResult:
    """Resultado del análisis del sensor"""
    status: SensorStatus
    alert_type: AlertType
    prediction: str
    message: str
    confidence: float
    severity: str
    
    # Métricas numéricas
    slope: float
    volatility: float
    drift_index: float
    noise_level: float
    
    # Predicción
    time_to_threshold: Optional[str]
    predicted_value: Optional[float]
    
    # Valores actuales
    current_value: float
    avg_value: float
    max_threshold: float
    min_threshold: float
    
    # Metadatos
    readings_analyzed: int
    analysis_window_minutes: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario"""
        return {
            "status": self.status.value,
            "alert_type": self.alert_type.value,
            "prediction": self.prediction,
            "message": self.message,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "slope": round(self.slope, 4),
            "volatility": round(self.volatility, 4),
            "drift_index": round(self.drift_index, 4),
            "noise_level": round(self.noise_level, 4),
            "time_to_threshold": self.time_to_threshold,
            "predicted_value": round(self.predicted_value, 2) if self.predicted_value else None,
            "current_value": round(self.current_value, 2),
            "avg_value": round(self.avg_value, 2),
            "max_threshold": round(self.max_threshold, 2),
            "min_threshold": round(self.min_threshold, 2),
            "readings_analyzed": self.readings_analyzed,
            "analysis_window_minutes": round(self.analysis_window_minutes, 2)
        }


class SensorAnalyzer:
    """
    Analizador avanzado de sensores con detección de anomalías
    y predicción de comportamiento.
    """
    
    MIN_READINGS = 20
    RECOMMENDED_READINGS = 50
    DRIFT_THRESHOLD = 0.15
    NOISE_CV_THRESHOLD = 0.30
    ZSCORE_THRESHOLD = 2.5
    PREDICTION_HORIZON_MINUTES = 60
    
    def __init__(self, readings: List[Any], max_threshold: float, min_threshold: float = 0):
        self.readings = readings
        self.max_threshold = max_threshold
        self.min_threshold = min_threshold
        self.sensor_range = max_threshold - min_threshold
        
        self.values = np.array([r.value for r in readings])
        self.timestamps = np.array([r.timestamp for r in readings]) if readings and hasattr(readings[0], 'timestamp') else None
        
        if self.timestamps is not None and len(self.timestamps) > 1:
            time_diff = (self.timestamps[-1] - self.timestamps[0]).total_seconds() / 60
            self.analysis_window = max(time_diff, 1)
        else:
            self.analysis_window = len(self.values) * 5 / 60
            
    def analyze(self) -> AnalysisResult:
        n = len(self.values)
        
        if n < self.MIN_READINGS:
            return self._insufficient_data_result()
        
        metrics = self._calculate_metrics()
        issues = self._detect_issues(metrics)
        prediction = self._predict_threshold_crossing(metrics)
        
        return self._determine_status(issues, prediction, metrics)
    
    def _insufficient_data_result(self) -> AnalysisResult:
        return AnalysisResult(
            status=SensorStatus.INICIANDO,
            alert_type=AlertType.OK,
            prediction="Iniciando",
            message=f"Se necesitan al menos {self.MIN_READINGS} lecturas para análisis predictivo. Lecturas actuales: {len(self.values)}",
            confidence=0.0,
            severity="info",
            slope=0.0,
            volatility=0.0,
            drift_index=0.0,
            noise_level=0.0,
            time_to_threshold=None,
            predicted_value=None,
            current_value=self.values[-1] if len(self.values) > 0 else 0,
            avg_value=np.mean(self.values) if len(self.values) > 0 else 0,
            max_threshold=self.max_threshold,
            min_threshold=self.min_threshold,
            readings_analyzed=len(self.values),
            analysis_window_minutes=self.analysis_window
        )
    
    def _calculate_metrics(self) -> Dict[str, float]:
        values = self.values
        n = len(values)
        
        current = values[-1]
        mean_val = np.mean(values)
        median_val = np.median(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        
        cv = std_val / mean_val if mean_val != 0 else 0
        
        X = np.arange(n).reshape(-1, 1)
        try:
            theil_model = TheilSenRegressor(random_state=42)
            theil_model.fit(X, values)
            slope = theil_model.coef_[0]
            
            lr_model = LinearRegression()
            lr_model.fit(X, values)
            lr_slope = lr_model.coef_[0]
            
            slope = (slope + lr_slope) / 2
        except:
            slope = 0
        
        half = n // 2
        if half > 2:
            first_half_mean = np.mean(values[:half])
            second_half_mean = np.mean(values[half:])
            drift = (second_half_mean - first_half_mean) / self.sensor_range if self.sensor_range > 0 else 0
        else:
            drift = 0
        
        alpha = 0.3
        ema = [values[0]]
        for v in values[1:]:
            ema.append(alpha * v + (1 - alpha) * ema[-1])
        ema = np.array(ema)
        ema_diff = ema[-1] - ema[0]
        
        z_scores = np.abs((values - mean_val) / std_val) if std_val > 0 else np.zeros_like(values)
        max_zscore = np.max(z_scores)
        anomaly_count = np.sum(z_scores > self.ZSCORE_THRESHOLD)
        
        unique_ratio = len(np.unique(values)) / n
        is_stuck = unique_ratio < 0.1 and std_val < 0.01
        is_disconnected = mean_val < (self.min_threshold * 0.05)
        
        readings_per_minute = n / self.analysis_window if self.analysis_window > 0 else 12
        future_readings = int(self.PREDICTION_HORIZON_MINUTES * readings_per_minute)
        future_X = np.array([n + i for i in range(future_readings)]).reshape(-1, 1)
        
        try:
            predicted_values = theil_model.predict(future_X)
        except:
            predicted_values = np.full(future_readings, mean_val)
        predicted_value = np.mean(predicted_values)
        
        return {
            'current': current,
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'min': min_val,
            'max': max_val,
            'cv': cv,
            'slope': slope,
            'drift': drift,
            'ema_diff': ema_diff,
            'max_zscore': max_zscore,
            'anomaly_count': anomaly_count,
            'is_stuck': is_stuck,
            'is_disconnected': is_disconnected,
            'unique_ratio': unique_ratio,
            'predicted_value': predicted_value,
            'n': n
        }
    
    def _detect_issues(self, metrics: Dict[str, float]) -> List[Tuple[AlertType, str, float]]:
        issues = []
        
        if metrics['is_stuck']:
            issues.append((
                AlertType.SENSOR_ATASCADO,
                "El sensor reporta valores idénticos. Posible sensor atascado o desconectado.",
                0.95
            ))
        
        if metrics['is_disconnected']:
            issues.append((
                AlertType.SENSOR_DESCONECTADO,
                "Valores cercanos a cero detectados. Posible sensor desconectado.",
                0.95
            ))
        
        if metrics['cv'] > self.NOISE_CV_THRESHOLD:
            severity = min(1.0, (metrics['cv'] - self.NOISE_CV_THRESHOLD) / 0.3 + 0.5)
            issues.append((
                AlertType.RUIDO_EXCESIVO,
                f"Ruido excesivo detectado (CV: {metrics['cv']*100:.1f}%). Revisar conexión física del sensor.",
                severity
            ))
        
        if metrics['drift'] > self.DRIFT_THRESHOLD:
            severity = min(1.0, metrics['drift'] / 0.3)
            issues.append((
                AlertType.DERIVA_POSITIVA,
                f"Deriva positiva detectada (+{metrics['drift']*100:.1f}%). Los valores están aumentando progresivamente.",
                severity
            ))
        
        if metrics['drift'] < -self.DRIFT_THRESHOLD:
            severity = min(1.0, abs(metrics['drift']) / 0.3)
            issues.append((
                AlertType.DERIVA_NEGATIVA,
                f"Deriva negativa detectada ({metrics['drift']*100:.1f}%). Los valores están disminuyendo progresivamente.",
                severity
            ))
        
        current = metrics['current']
        
        if current > self.max_threshold:
            severity = min(1.0, (current - self.max_threshold) / self.sensor_range + 0.5)
            issues.append((
                AlertType.UMBRAL_MAX,
                f"LECTURA ACTUAL SUPERA el umbral máximo ({current:.1f} > {self.max_threshold}).",
                severity
            ))
        
        if current < self.min_threshold:
            severity = min(1.0, (self.min_threshold - current) / self.sensor_range + 0.5)
            issues.append((
                AlertType.UMBRAL_MIN,
                f"LECTURA ACTUAL bajo el umbral mínimo ({current:.1f} < {self.min_threshold}).",
                severity
            ))
        
        return issues
    
    def _predict_threshold_crossing(self, metrics: Dict[str, float]) -> Optional[Dict[str, Any]]:
        current = metrics['current']
        n = metrics['n']
        
        if n < 20:
            return None
        
        values = self.values
        half = n // 2
        first_half_mean = np.mean(values[:half])
        second_half_mean = np.mean(values[half:])
        
        ema_trend = metrics.get('ema_diff', 0)
        
        is_uptrend = second_half_mean > first_half_mean * 1.1
        is_downtrend = second_half_mean < first_half_mean * 0.9
        
        readings_per_minute = n / self.analysis_window if self.analysis_window > 0 else 12
        
        if is_uptrend and current < self.max_threshold:
            threshold_gap = self.max_threshold - current
            avg_increase_per_reading = (second_half_mean - first_half_mean) / half
            
            if avg_increase_per_reading > 0:
                readings_to_threshold = threshold_gap / avg_increase_per_reading
                minutes_to_max = readings_to_threshold / readings_per_minute
                
                if 0 < minutes_to_max < self.PREDICTION_HORIZON_MINUTES:
                    confidence = self._calculate_prediction_confidence(metrics, 'max')
                    if confidence >= 0.5:
                        return {
                            'type': 'max',
                            'threshold': self.max_threshold,
                            'predicted_value': metrics['predicted_value'],
                            'minutes': int(minutes_to_max),
                            'confidence': confidence
                        }
        
        if is_downtrend and current > self.min_threshold:
            threshold_gap = current - self.min_threshold
            avg_decrease_per_reading = (first_half_mean - second_half_mean) / half
            
            if avg_decrease_per_reading > 0:
                readings_to_threshold = threshold_gap / avg_decrease_per_reading
                minutes_to_min = readings_to_threshold / readings_per_minute
                
                if 0 < minutes_to_min < self.PREDICTION_HORIZON_MINUTES:
                    confidence = self._calculate_prediction_confidence(metrics, 'min')
                    if confidence >= 0.5:
                        return {
                            'type': 'min',
                            'threshold': self.min_threshold,
                            'predicted_value': metrics['predicted_value'],
                            'minutes': int(minutes_to_min),
                            'confidence': confidence
                        }
        
        return None
    
    def _calculate_prediction_confidence(self, metrics: Dict[str, float], threshold_type: str) -> float:
        confidence = 1.0
        confidence *= (1 - min(0.5, metrics['cv']))
        anomaly_ratio = metrics['anomaly_count'] / metrics['n']
        confidence *= (1 - min(0.3, anomaly_ratio))
        if abs(metrics['slope']) > 0.1:
            confidence *= 1.1
        return max(0.1, min(1.0, confidence))
    
    def _determine_status(self, issues: List[Tuple[AlertType, str, float]], 
                         prediction: Optional[Dict[str, Any]],
                         metrics: Dict[str, float]) -> AnalysisResult:
        
        critical_issues = [i for i in issues if i[2] >= 0.7]
        
        if critical_issues:
            issue = critical_issues[0]
            alert_type = issue[0]
            message = issue[1]
            confidence = issue[2]
            
            if 'Atascado' in alert_type.value or 'Desconectado' in alert_type.value:
                status = SensorStatus.CRITICO
                severity = "critical"
                prediction_text = "Fallo de Sensor"
            elif 'Ruido' in alert_type.value:
                status = SensorStatus.ALERTA
                severity = "critical"
                prediction_text = "Sensor Inestable"
            elif 'Umbral' in alert_type.value and 'Predicción' not in alert_type.value:
                status = SensorStatus.CRITICO
                severity = "critical"
                prediction_text = "Umbral Superado"
            else:
                status = SensorStatus.ALERTA
                severity = "critical"
                prediction_text = "Deriva Detectada"
        
        elif prediction:
            if prediction['type'] == 'max':
                alert_type = AlertType.PREDICCION_MAX
                prediction_text = "Predicción Umbral Máximo"
            else:
                alert_type = AlertType.PREDICCION_MIN
                prediction_text = "Predicción Umbral Mínimo"
            
            message = f"Se predice que el sensor superará el umbral en {prediction['minutes']} minutos. Valor actual: {metrics['current']:.1f}, Predicho: {prediction['predicted_value']:.1f}"
            confidence = prediction['confidence']
            status = SensorStatus.ADVERTENCIA
            severity = "warning"
        
        elif issues:
            issue = issues[0]
            alert_type = issue[0]
            message = issue[1]
            confidence = issue[2]
            status = SensorStatus.ADVERTENCIA
            severity = "warning"
            prediction_text = "Advertencia"
        
        else:
            alert_type = AlertType.OK
            message = "El sensor opera dentro de parámetros normales."
            confidence = 0.95
            status = SensorStatus.ESTABLE
            severity = "info"
            prediction_text = "Estable"
        
        if prediction:
            mins = prediction['minutes']
            if mins >= 1:
                time_to_threshold = f"{mins} min"
            else:
                seconds = mins * 60
                time_to_threshold = f"{int(seconds)} seg"
        else:
            time_to_threshold = None
        
        return AnalysisResult(
            status=status,
            alert_type=alert_type,
            prediction=prediction_text,
            message=message,
            confidence=confidence,
            severity=severity,
            slope=metrics['slope'],
            volatility=metrics['cv'],
            drift_index=metrics['drift'],
            noise_level=metrics['cv'],
            time_to_threshold=time_to_threshold,
            predicted_value=prediction['predicted_value'] if prediction else None,
            current_value=metrics['current'],
            avg_value=metrics['mean'],
            max_threshold=self.max_threshold,
            min_threshold=self.min_threshold,
            readings_analyzed=metrics['n'],
            analysis_window_minutes=self.analysis_window
        )


def predict_sensor_failure(
    recent_readings: List[Any],
    max_threshold: float = 100,
    min_threshold: float = 0
) -> Dict[str, Any]:
    """
    Función principal para predecir fallos del sensor.
    """
    analyzer = SensorAnalyzer(
        readings=recent_readings,
        max_threshold=max_threshold,
        min_threshold=min_threshold
    )
    
    result = analyzer.analyze()
    
    return result.to_dict()


def predict_sensor_failure_legacy(recent_readings: List[Any]) -> Dict[str, Any]:
    """
    Versión legacy para compatibilidad.
    Asume umbrales por defecto (0-100).
    """
    return predict_sensor_failure(recent_readings, 100, 0)
