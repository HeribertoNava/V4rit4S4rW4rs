import serial
import time
import csv

# Configuración del puerto serial
port = "COM4"
baudrate = 115200

def capture_data(figura):
    csv_filename = f'datos_{figura}.csv'
    ser = serial.Serial(port, baudrate)
    time.sleep(2)
    all_data = []
    capturing = False

    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if not capturing and "CAPTURE_START" not in line:
                continue  # No hacer nada si no estamos capturando

            print(f"Línea recibida: {line}")

            if "CAPTURE_START" in line:
                capturing = True
                all_data = []
                print("Iniciando captura...")

            elif "CAPTURE_COMPLETE" in line:
                capturing = False
                print(f"Captura completa. {len(all_data)} muestras capturadas.")
                
                save_capture = input("Presiona 's' para guardar la captura o 'd' para descartarla: ")

                if save_capture.lower() == 's':
                    with open(csv_filename, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if file.tell() == 0:
                            writer.writerow(["ax", "ay", "az", "gx", "gy", "gz", "label"])
                        for data in all_data:
                            writer.writerow(data + [figura])
                        writer.writerow([])
                    print("Datos guardados en el archivo CSV.")
                else:
                    print("Captura descartada.")
                all_data = []  # Reiniciar datos para la próxima captura
                break  # Salir después de guardar o descartar

            elif capturing and line.startswith("DATA,"):
                parts = line.split(",")
                if len(parts) == 7:
                    data = [float(value) for value in parts[1:]]
                    all_data.append(data)
                    print(f"Muestra capturada: {data}")
                else:
                    print(f"Línea de datos incompleta: {line}")

        except ValueError as e:
            print(f"Error al convertir los datos: {e}, data: {line}")
        except KeyboardInterrupt:
            break

    ser.close()
    print("Desconectado...")

def main():
    while True:
        print("Selecciona la figura: 'e' para equis, 'c' para C, 'l' para ele, 'i' para infinito, 'd' para diagonal, o 'esc' para salir.")
        figura = input("Ingresa una opción: ").lower()
        
        if figura == 'e':
            print("Capturando datos para equis")
            capture_data('equis')
        elif figura == 'c':
            print("Capturando datos para C")
            capture_data('C')
        elif figura == 'l':
            print("Capturando datos para ele")
            capture_data('ele')
        elif figura == 'i':
            print("Capturando datos para infinito")
            capture_data('infinito')
        elif figura == 'd':
            print("Capturando datos para diagonal")
            capture_data('diagonal')
        elif figura == 'esc':
            break
        else:
            print("Opción no válida. Inténtalo nuevamente.")

if __name__ == "__main__":
    main()
