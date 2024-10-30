import serial
import time
import numpy as np
import joblib
from collections import deque
import pandas as pd

# Cargar el modelo
clf = joblib.load('modeloCuadrado.pkl')

# Configuración del puerto serial
port = "COM4"
baudrate = 115200

# Inicializa la conexión serial
ser = serial.Serial(port, baudrate)
time.sleep(2)

# Parámetros para la ventana deslizante y el filtro de predicciones
window_size = 120
prediction_buffer = deque(maxlen=5)

def extract_features(segment):
    means = np.mean(segment, axis=0)
    stds = np.std(segment, axis=0)
    maxs = np.max(segment, axis=0)
    mins = np.min(segment, axis=0)
    feature_vector = np.concatenate([means, stds, maxs, mins])
    return feature_vector

def normalize_data(data, scaler):
    if isinstance(data, list):
        data = np.array(data)
    return scaler.transform(data.reshape(1, -1)).flatten()

def classify_movement(model, segment, scaler):
    segment = np.array(segment)
    column_names = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    normalized_segment = pd.DataFrame(segment, columns=column_names)
    normalized_segment = scaler.transform(normalized_segment)
    features = extract_features(normalized_segment).reshape(1, -1)
    return model.predict(features)[0]

def get_filtered_prediction(predictions):
    if len(predictions) < prediction_buffer.maxlen:
        return None
    return max(set(predictions), key=predictions.count)

def read_and_classify():
    scaler = joblib.load('scaler_cuadrado.pkl')
    current_window = deque(maxlen=window_size)
    
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if line.startswith("DATA,"):
                parts = line.split(",")
                if len(parts) == 7:
                    data = [float(value) for value in parts[1:]]
                    current_window.append(data)
                    
                    if len(current_window) == window_size:
                        prediction = classify_movement(clf, np.array(current_window), scaler)
                        prediction_buffer.append(prediction)
                        
                        filtered_prediction = get_filtered_prediction(prediction_buffer)
                        if filtered_prediction is not None:
                            if filtered_prediction == 1.0:
                                print("Es un cuadrado")
                            else:
                                print("No es un cuadrado")
            
        except ValueError as e:
            print(f"Error al convertir los datos: {e}, data: {line}")
        except KeyboardInterrupt:
            break
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")
            time.sleep(1)

    ser.close()
    print("Desconectado...")

try:
    read_and_classify()
except KeyboardInterrupt:
    print("Interrupción del usuario")
finally:
    if ser.is_open:
        ser.close()
    print("Desconectado...")
