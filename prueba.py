import serial

# Configura el puerto serial (ajusta el 'COM3' según tu sistema, por ejemplo, '/dev/ttyUSB0' en Linux)
serial_port = "COM4"  # Cambia esto al puerto correcto
baud_rate = 115200    # Asegúrate de que coincida con el de la ESP32

# Inicia la conexión serial
ser = serial.Serial(serial_port, baud_rate)
capturing = False

try:
    print("Conectado al puerto serial. Esperando datos...")
    
    while True:
        if ser.in_waiting > 0:
            # Lee la línea de datos desde la ESP32
            line = ser.readline().decode('utf-8').strip()
            
            if line == "CAPTURE_START":
                capturing = True
                print("Iniciando captura de datos...")
                
            elif line == "CAPTURE_COMPLETE":
                capturing = False
                print("Captura de datos completada.")
                
            elif capturing:
                # Muestra los datos del giroscopio si estamos capturando
                print("Datos del giroscopio:", line)

except KeyboardInterrupt:
    print("Interrumpido por el usuario.")

finally:
    # Cierra el puerto serial
    ser.close()
    print("Conexión serial cerrada.")
