import serial
import time
import numpy as np
import joblib
from collections import deque
import pandas as pd
from sklearn.neural_network import MLPClassifier
import pyttsx3
import paho.mqtt.client as mqtt

model = joblib.load('modelo_figuras_mlp.pkl')
scaler = joblib.load('scaler_figuras_mlp.pkl')

# Configuración del puerto serial y del cliente MQTT
port = "COM4"
baudrate = 115200
engine = pyttsx3.init()
mqtt_client = mqtt.Client()
mqtt_client.connect("broker.emqx.io", 1883, 60)

ser = serial.Serial(port, baudrate)
time.sleep(2)

window_size = 60
prediction_buffer = deque(maxlen=5)

def extract_features(segment):
    means = np.mean(segment, axis=0)
    stds = np.std(segment, axis=0)
    maxs = np.max(segment, axis=0)
    mins = np.min(segment, axis=0)
    feature_vector = np.concatenate([means, stds, maxs, mins])
    return feature_vector 

def classify_movement(model, segment, scaler):
    segment = np.array(segment)
    column_names = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    normalized_segment = pd.DataFrame(segment, columns=column_names)
    normalized_segment = scaler.transform(normalized_segment)
    features = extract_features(normalized_segment).reshape(1, -1)
    return model.predict(features)[0]

def send_mqtt_message(prediction):
    mqtt_client.publish("esp32/figura", prediction)

def read_and_classify():
    while True:
        current_window = deque(maxlen=window_size)
        capturing = False
        
        while not capturing:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Espera a la señal para iniciar captura
                if line == "CAPTURE_START":
                    capturing = True
                    current_window.clear()
                    prediction_buffer.clear()
                    print("Iniciando captura...")

            except ValueError as e:
                print(f"Error al convertir los datos: {e}, data: {line}")
            except serial.SerialException as e:
                print(f"Error de conexión serial: {e}")
                time.sleep(1)
        
        # Captura y clasificación
        while capturing:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line == "CAPTURE_COMPLETE":
                    capturing = False
                    if current_window:
                        final_prediction = classify_movement(model, np.array(current_window), scaler)
                        print(f"Es un {final_prediction}")
                        engine.say(final_prediction)
                        engine.runAndWait()
                        send_mqtt_message(final_prediction)  # Enviar palabra clave por MQTT
                    print("Captura completa. Esperando botón para iniciar nueva captura.")
                
                elif line.startswith("DATA,"):
                    parts = line.split(",")
                    if len(parts) == 7:
                        data = [float(value) for value in parts[1:]]
                        current_window.append(data)
                
            except ValueError as e:
                print(f"Error al convertir los datos: {e}, data: {line}")
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
