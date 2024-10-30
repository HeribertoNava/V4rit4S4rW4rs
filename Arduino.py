from threading import Thread
from collections import deque
import serial
import time
import sys
import csv

class Arduino:
    def __init__(self, port, num_metrics=1, max_samples=20, baudrate=115200, serial_timeout=1.0):
        self.port_ = port
        self.baudrate_ = baudrate
        self.serial_ = None
        self.serial_timeout = serial_timeout
        self.thread_ = None
        self.isReceiving_ = False
        self.isRun_ = False
        self.num_metrics_ = num_metrics
        self.max_samples_ = max_samples
        self.data_ = []
        
        self.init_params_()
        
    def init_params_(self):
        for i in range(self.num_metrics_):
            self.data_.append(deque([0] * self.max_samples_, maxlen=self.max_samples_))
        
    def start(self):
        print(f"Intentando conectar al puerto {self.port_}")
        
        try:
            self.serial_ = serial.Serial(self.port_, baudrate=self.baudrate_, timeout=self.serial_timeout)
            print(f"Conexión establecida con {self.port_}")
            self.thread_ = Thread(target=self.background_read_)
            self.thread_.start()
            self.isRun_ = True
            print("Conectado...");
        except:
            sys.exit("Failed to connect with " + str(self.port_))

    def get_serial_data(self, frame, lines, lineValueText, lineLabel, pltNumber):
        data = self.data_[pltNumber]
        lines.set_data(range(self.max_samples_), data)

    def background_read_(self):
        time.sleep(1.0)
        if self.serial_:
            self.serial_.flushInput()
            while self.isRun_:
                line = self.serial_.readline()
                if line:
                    try:
                        raw_data = line.decode().strip().split(",")
                        if raw_data[0] == "DATA":
                            for i in range(self.num_metrics_):
                                self.data_[i].append(float(raw_data[i+1]))
                    except ValueError as e:
                        print(f"Error al convertir los datos: {e}, data: {line.decode().strip()}")
    
    def get_data(self, index):
        if index not in [i for i in range(self.num_metrics_)]:
            print("El índice no es correcto")
        else:
            return list(self.data_[index])
    
    def close(self):
        self.isRun_ = False
        if self.thread_ is None:
            pass
        else:
            self.thread_.join()
        
        if self.serial_ is None:
            pass
        else:
            self.serial_.close()
        print("Desconectado...")

# Configuración del puerto serial y archivo CSV
port = "COM5"  # Cambia esto por el puerto correcto en tu sistema
csv_filename = "mpu6050_data.csv"

# Inicializa el objeto Arduino
a = Arduino(port, num_metrics=6, max_samples=50, baudrate=115200)
a.start()

# Espera un momento para asegurar la conexión
time.sleep(2)

def ask_user_to_save():
    while True:
        response = input("¿Quieres guardar la captura? (Sí/No): ").strip().lower()
        if response in ["sí", "si", "s"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("Respuesta no válida. Por favor, responde con 'Sí' o 'No'.")

def read_and_save_data():
    all_data = []
    capturing = False
    
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ax", "ay", "az", "gx", "gy", "gz"])  # Escribir encabezados

        while True:
            try:
                line = a.serial_.readline().decode('utf-8', errors='ignore').strip()
                print(f"Línea recibida: {line}")
                if line == "CAPTURE_COMPLETE":
                    capturing = True
                    print("Iniciando captura de datos...")
                elif line == "CAPTURE_COMPLETE":
                    capturing = False

                    if ask_user_to_save():
                        for data in all_data:
                            writer.writerow(data)
                        print("Captura guardada.")
                    else:
                        print("Captura descartada.")
                    all_data = []  # Reiniciar los datos almacenados para la próxima captura
                elif line.startswith("DATA,"):
                    data = [float(value) for value in line.split(",")[1:] if value]
                    all_data.append(data)
                    print(f"Datos guardados temporalmente: {data}")
            except ValueError as e:
                print(f"Error al convertir los datos: {e}, data: {line}")

try:
    read_and_save_data()
except KeyboardInterrupt:
    print("Interrupción del usuario")
finally:
    a.close()
