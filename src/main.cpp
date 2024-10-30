#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const int buttonPin = 15  ; // GPIO18
bool buttonState = HIGH;
bool lastButtonState = HIGH;
bool capturing = false;
int sampleCount = 0;

// Pines para los LEDs
#define PIN_LED_1 16 // LED inferior
#define PIN_LED_2 17 // LED medio inferior
#define PIN_LED_3 18 // LED medio superior
#define PIN_LED_4 19 // LED superior

void calibrateMPU() {
  mpu.CalibrateAccel(6);
  mpu.CalibrateGyro(6);
  mpu.PrintActiveOffsets();
  Serial.println("Calibración completada");
}

void readMPU() {
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  Serial.print("DATA,");
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);
}

void progressiveLEDs() {
  for (int brightness = 0; brightness <= 255; brightness += 5) {
    analogWrite(PIN_LED_4, brightness);
    delay(20);
    if (brightness >= 85) {
      analogWrite(PIN_LED_1, brightness);
      delay(20);
    }
    if (brightness >= 170) {
      analogWrite(PIN_LED_2, brightness);
      delay(20);
    }
    if (brightness >= 200) {
      analogWrite(PIN_LED_3, brightness);
      delay(20);
    }
  }
}

void vibrationEffect() {
  for (int i = 0; i < 10; i++) {
    analogWrite(PIN_LED_1, 220);
    analogWrite(PIN_LED_2, 240);
    analogWrite(PIN_LED_3, 255);
    analogWrite(PIN_LED_4, 255);
    delay(50);

    analogWrite(PIN_LED_1, 180);
    analogWrite(PIN_LED_2, 200);
    analogWrite(PIN_LED_3, 220);
    analogWrite(PIN_LED_4, 220);
    delay(50);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Reset");

  Wire.begin(21, 22); // SDA -> GPIO21, SCL -> GPIO22
  Wire.setClock(400000); // Configura I2C a 400kHz

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(PIN_LED_1, OUTPUT);
  pinMode(PIN_LED_2, OUTPUT);
  pinMode(PIN_LED_3, OUTPUT);
  pinMode(PIN_LED_4, OUTPUT);

  mpu.initialize();
  if (mpu.testConnection()) {
    Serial.println("MPU6050 conectado correctamente.");
    calibrateMPU();
  } else {
    Serial.println("Error al conectar el MPU6050.");
    while (1);
  }
}

void loop() {
  buttonState = digitalRead(buttonPin);

  // Iniciar o detener la captura al presionar el botón
  if (buttonState == LOW && lastButtonState == HIGH) {
    capturing = !capturing;
    if (capturing) {
      Serial.println("CAPTURE_START");
      sampleCount = 0;
      progressiveLEDs(); // Enciende LEDs de forma progresiva cuando inicia la captura
    } else {
      Serial.println("CAPTURE_COMPLETE");
      vibrationEffect(); // Efecto de vibración de LEDs al finalizar la captura
    }
    delay(200);
  }

  // Realizar la captura de datos del giroscopio si capturing está activo
  if (capturing) {
    if (sampleCount < 40) {
      readMPU();
      sampleCount++;
    } else {
      Serial.println("CAPTURE_COMPLETE");
      capturing = false;
      vibrationEffect();
    }
    delay(50);
  }

  lastButtonState = buttonState;
}
