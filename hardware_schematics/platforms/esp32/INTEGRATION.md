# ESP32 Platform Integration Guide

**Platform:** ESP32-S3, ESP32-C6, ESP32 (original)  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready

---

## Overview

This guide provides comprehensive integration strategies for deploying Project-AI Pip-Boy variants on ESP32 microcontrollers. Covers ultra-low-power operation, WiFi/BLE connectivity, sensor integration, and deployment configurations for ESP32-S3 (recommended), ESP32-C6 (WiFi 6), and ESP32 (legacy) platforms.

**Key Advantages:**
- **Ultra-Low Power:** 10μA deep sleep, 160-240mA active (vs 700mA+ for Raspberry Pi)
- **Built-in WiFi/BLE:** 802.11 b/g/n + Bluetooth 5.0 (no external modules)
- **Cost-Effective:** $2-$8 per chip (vs $15-$80 for Raspberry Pi)
- **Compact:** 38mm x 26mm module (vs 85mm x 56mm Pi)
- **Real-Time OS:** FreeRTOS for deterministic operation

---

## Supported Models

### ESP32-S3 (Recommended)
- **CPU:** Xtensa LX7 dual-core @ 240MHz
- **RAM:** 512KB SRAM, 8MB PSRAM (optional)
- **Flash:** 4MB to 16MB (typically 8MB)
- **WiFi:** 802.11 b/g/n (2.4GHz), up to 150Mbps
- **Bluetooth:** BLE 5.0, Bluetooth Mesh
- **USB:** Native USB-OTG (no UART-to-USB bridge)
- **AI Acceleration:** Vector instructions for ML inference
- **Camera Interface:** DVP (parallel) up to 40MHz
- **Display Interface:** SPI, I2C, I8080 (8-bit parallel)
- **Power:** 10μA (deep sleep), 40mA (light sleep), 160mA (active WiFi)
- **Best For:** Low-power variants (Student, basic Enterprise)

### ESP32-C6 (WiFi 6 + Zigbee/Thread)
- **CPU:** RISC-V single-core @ 160MHz
- **RAM:** 512KB SRAM
- **Flash:** 4MB (typical)
- **WiFi:** 802.11ax (WiFi 6), 2.4GHz only
- **Bluetooth:** BLE 5.3
- **Zigbee/Thread:** IEEE 802.15.4 radio (smart home integration)
- **Power:** 7μA (deep sleep), 35mA (light sleep), 140mA (active)
- **Best For:** IoT integration, mesh networking, Matter protocol

### ESP32 (Original, Legacy)
- **CPU:** Xtensa LX6 dual-core @ 240MHz
- **RAM:** 520KB SRAM, 4MB PSRAM (external)
- **Flash:** 4MB (typical)
- **WiFi:** 802.11 b/g/n
- **Bluetooth:** Classic + BLE 4.2
- **Power:** 10μA (deep sleep), 800μA (light sleep), 160-260mA (active)
- **Best For:** Budget builds, legacy support

---

## Hardware Integration

### 1. Display Integration

#### 2.8" ILI9341 TFT Display (320x240, SPI)
**Recommended:** Adafruit 2.8" TFT Touch Shield

```cpp
// ESP32-S3 SPI pins (VSPI)
#define TFT_MISO 12
#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_CS   15
#define TFT_DC   2
#define TFT_RST  4

#include <TFT_eSPI.h>
TFT_eSPI tft = TFT_eSPI();

void setup() {
  tft.init();
  tft.setRotation(1);  // Landscape
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  tft.println("Project-AI Pip-Boy");
}
```

**Performance:**
- **SPI Speed:** 40MHz (ILI9341), 80MHz (ST7789)
- **Frame Rate:** 30fps (full screen), 60fps (partial updates)
- **Power Consumption:** 50-120mW (typical)

#### E-Paper Display (Low Power, for Student variant)
**Recommended:** Waveshare 2.9" E-Paper (296x128, SPI)

```cpp
#include <GxEPD2_BW.h>

GxEPD2_BW<GxEPD2_290, GxEPD2_290::HEIGHT> display(
  GxEPD2_290(/*CS=*/ 5, /*DC=*/ 17, /*RST=*/ 16, /*BUSY=*/ 4)
);

void setup() {
  display.init();
  display.setRotation(1);
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(GxEPD_BLACK);
  
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    display.setCursor(10, 30);
    display.print("Battery: 95%");
  } while (display.nextPage());
}
```

**Power Consumption:** <1mW (static image, no refresh)

### 2. Sensor Integration

#### I2C Sensors (Same as Raspberry Pi)
```cpp
#include <Wire.h>
#include <Adafruit_BMP3XX.h>
#include <Adafruit_SHT4x.h>

Adafruit_BMP3XX bmp;
Adafruit_SHT4x sht4;

void setup() {
  Wire.begin(21, 22);  // SDA=21, SCL=22 (default ESP32)
  
  if (!bmp.begin_I2C(0x76)) {
    Serial.println("BMP390 not found!");
  }
  
  if (!sht4.begin()) {
    Serial.println("SHT40 not found!");
  }
}

void loop() {
  bmp.performReading();
  sensors_event_t humidity, temp;
  sht4.getEvent(&humidity, &temp);
  
  Serial.printf("Temp: %.2f °C, Pressure: %.2f hPa, Humidity: %.2f %%\n",
                bmp.temperature, bmp.pressure / 100.0, humidity.relative_humidity);
  
  delay(2000);
}
```

#### ADC for Multimeter (Engineer variant)
**ESP32 Internal ADC:**
- **Resolution:** 12-bit (0-4095)
- **Voltage Range:** 0-3.3V (use voltage divider for higher voltages)
- **Accuracy:** ±2% (with calibration)
- **Channels:** 18 channels (ESP32-S3)

```cpp
#define VOLTAGE_PIN 34  // ADC1_CH6

void setup() {
  analogReadResolution(12);  // 12-bit ADC
  analogSetAttenuation(ADC_11db);  // 0-3.6V range
}

float readVoltage() {
  int raw = analogRead(VOLTAGE_PIN);
  float voltage = (raw / 4095.0) * 3.6;  // Convert to volts
  return voltage * 10;  // 10x voltage divider
}
```

**External ADC for Higher Precision:**
- **ADS1115:** 16-bit, 4-channel, I2C interface
- **MCP3208:** 12-bit, 8-channel, SPI interface

### 3. GPS Module Integration

#### UART GPS (Same wiring as Raspberry Pi)
```cpp
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>

TinyGPSPlus gps;
HardwareSerial GPS(1);  // UART1

void setup() {
  GPS.begin(9600, SERIAL_8N1, 16, 17);  // RX=16, TX=17
}

void loop() {
  while (GPS.available() > 0) {
    if (gps.encode(GPS.read())) {
      if (gps.location.isValid()) {
        Serial.printf("Lat: %.6f, Lon: %.6f, Alt: %.2f m\n",
                      gps.location.lat(), gps.location.lng(), gps.altitude.meters());
      }
    }
  }
}
```

### 4. WiFi & Bluetooth Integration

#### WiFi Station Mode (Connect to AP)
```cpp
#include <WiFi.h>

const char* ssid = "Project-AI";
const char* password = "secure_password";

void setup() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.printf("\nConnected! IP: %s\n", WiFi.localIP().toString().c_str());
}
```

#### BLE Beacon (Proximity Detection)
```cpp
#include <BLEDevice.h>
#include <BLEAdvertising.h>

void setup() {
  BLEDevice::init("Project-AI-Pip-Boy");
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  
  BLEAdvertisementData adData;
  adData.setName("Project-AI-Pip-Boy");
  adData.setManufacturerData("Project-AI");
  
  pAdvertising->setAdvertisementData(adData);
  pAdvertising->start();
}
```

### 5. Camera Integration (ESP32-S3 only)

#### OV2640 Camera Module
```cpp
#include "esp_camera.h"

#define PWDN_GPIO_NUM    -1
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    15
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      19
// ... (additional pins)

void setup() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  // ... (additional config)
  config.frame_size = FRAMESIZE_VGA;  // 640x480
  config.pixel_format = PIXFORMAT_JPEG;
  config.jpeg_quality = 12;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }
}

void captureImage() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  // Process image (fb->buf contains JPEG data, fb->len is size)
  Serial.printf("Image captured: %d bytes\n", fb->len);
  
  esp_camera_fb_return(fb);
}
```

---

## Power Management

### Deep Sleep Mode (Ultra-Low Power)

```cpp
#include "esp_sleep.h"

#define BUTTON_PIN 33  // Wake button (GPIO33)
#define SLEEP_TIME_US (30 * 1000000)  // 30 seconds

void goToSleep() {
  // Wake on button press (GPIO33 LOW)
  esp_sleep_enable_ext0_wakeup((gpio_num_t)BUTTON_PIN, 0);
  
  // Or wake after timer
  esp_sleep_enable_timer_wakeup(SLEEP_TIME_US);
  
  Serial.println("Entering deep sleep...");
  esp_deep_sleep_start();
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Check wake reason
  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_EXT0:
      Serial.println("Woken by button");
      break;
    case ESP_SLEEP_WAKEUP_TIMER:
      Serial.println("Woken by timer");
      break;
    default:
      Serial.println("Power-on reset");
      break;
  }
}
```

### Light Sleep Mode (Fast Wake)
```cpp
void lightSleep() {
  // Configure wake sources
  gpio_wakeup_enable((gpio_num_t)BUTTON_PIN, GPIO_INTR_LOW_LEVEL);
  esp_sleep_enable_gpio_wakeup();
  
  // Enter light sleep (WiFi/BLE suspended, RAM retained)
  esp_light_sleep_start();
  
  // Execution resumes here after wake
  Serial.println("Woke from light sleep");
}
```

### Power Consumption Measurements

| Mode | Current (ESP32-S3) | Battery Life (3000mAh) |
|------|--------------------|------------------------|
| Deep Sleep | 10μA | ~34 years |
| Light Sleep | 800μA | ~156 days |
| Idle (WiFi off) | 30mA | ~4 days |
| Active (WiFi on) | 160mA | ~18 hours |
| Active (WiFi TX) | 240mA | ~12 hours |

---

## AI Model Deployment

### TensorFlow Lite Micro (Embedded ML)

```cpp
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "model_data.h"  // Converted .tflite model

constexpr int kTensorArenaSize = 60 * 1024;  // 60KB
uint8_t tensor_arena[kTensorArenaSize];

void setup() {
  // Load model
  const tflite::Model* model = tflite::GetModel(model_data);
  
  // Create interpreter
  static tflite::MicroInterpreter static_interpreter(
    model, tflite::AllOpsResolver(), tensor_arena, kTensorArenaSize
  );
  
  // Allocate tensors
  static_interpreter.AllocateTensors();
  
  // Get input tensor
  TfLiteTensor* input = static_interpreter.input(0);
  
  // Fill input (example: 224x224 image)
  for (int i = 0; i < input->bytes; i++) {
    input->data.uint8[i] = random(0, 255);
  }
  
  // Run inference
  static_interpreter.Invoke();
  
  // Get output
  TfLiteTensor* output = static_interpreter.output(0);
  Serial.printf("Output: %f\n", output->data.f[0]);
}
```

**Performance Benchmarks (MobileNetV2, 96x96 input):**
- **ESP32-S3 (240MHz):** 850ms/inference
- **ESP32 (240MHz):** 1200ms/inference

### Edge Impulse Integration
**Optimized for ESP32:**
- **Audio Classification:** Wake word detection, gunshot detection
- **Sensor Fusion:** IMU-based gesture recognition
- **Anomaly Detection:** Equipment fault detection

```cpp
#include <Your_Model_inferencing.h>

void runInference() {
  signal_t signal;
  signal.total_length = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE;
  signal.get_data = &raw_feature_get_data;
  
  ei_impulse_result_t result = {0};
  EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
  
  if (res != EI_IMPULSE_OK) {
    Serial.printf("Error: %d\n", res);
    return;
  }
  
  // Print results
  for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
    Serial.printf("%s: %.5f\n", 
                  result.classification[ix].label,
                  result.classification[ix].value);
  }
}
```

---

## Operating System Configuration

### ESP-IDF (Espressif IoT Development Framework)
**Recommended for production deployments**

```bash
# Install ESP-IDF
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32,esp32s3,esp32c6

# Activate environment
. ./export.sh

# Create project
idf.py create-project project-ai-pipboy
cd project-ai-pipboy

# Configure
idf.py menuconfig

# Build & flash
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

### Arduino IDE (Rapid Prototyping)
**Best for beginners, quick testing**

```bash
# Add ESP32 board manager URL (Arduino IDE)
https://espressif.github.io/arduino-esp32/package_esp32_index.json

# Install board: Tools -> Board -> Boards Manager -> "esp32"
# Select board: Tools -> Board -> ESP32 Arduino -> ESP32-S3 Dev Module
# Flash: Sketch -> Upload
```

### PlatformIO (Professional Development)
**Best for multi-platform projects, CI/CD**

```ini
; platformio.ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
lib_deps =
    bodmer/TFT_eSPI@^2.5.0
    adafruit/Adafruit BMP3XX Library@^2.1.0
    mikalhart/TinyGPSPlus@^1.0.3
```

---

## Deployment Configurations

### Configuration 1: ESP32-S3 + Student Variant
**Components:**
- ESP32-S3-DevKitC-1 (8MB Flash, 2MB PSRAM)
- 2.8" ILI9341 TFT (320x240 SPI)
- Basic sensors (BMP390, SHT40)
- 2000mAh Li-Po battery
- TP4056 charger module

**Power:** 2-4W (typical use)  
**Battery Life:** 8-16 hours  
**Cost:** $35 (ESP32-S3 $8 + display $15 + sensors $5 + battery $5 + misc $2)

### Configuration 2: ESP32-C6 + IoT Variant
**Components:**
- ESP32-C6-DevKitC-1
- E-Paper 2.9" (low power display)
- Environmental sensors (air quality, temp, humidity)
- Zigbee/Thread smart home integration
- 1500mAh battery

**Power:** 1-2W (typical)  
**Battery Life:** 24-48 hours  
**Cost:** $30

### Configuration 3: ESP32 + Budget Variant
**Components:**
- ESP32-WROOM-32 (legacy)
- 2.4" TFT (ST7789)
- Minimal sensors
- 1000mAh battery

**Power:** 1.5-3W  
**Battery Life:** 5-10 hours  
**Cost:** $18

---

## Appendix A: Pin Mapping Table

### ESP32-S3 GPIO Allocation
| Pin | Function | Device | Notes |
|-----|----------|--------|-------|
| GPIO1 | ADC | Voltage sensor | 12-bit ADC |
| GPIO2 | Output | Display DC | |
| GPIO4 | Output | Display RST | |
| GPIO5 | Output | Display CS | |
| GPIO13 | SPI MOSI | Display | VSPI |
| GPIO14 | SPI CLK | Display | VSPI |
| GPIO15 | SPI CS | SD Card | |
| GPIO16 | UART RX | GPS | UART1 |
| GPIO17 | UART TX | GPS | UART1 |
| GPIO21 | I2C SDA | Sensors | |
| GPIO22 | I2C SCL | Sensors | |
| GPIO33 | Input | Wake button | |

---

## Appendix B: OTA Firmware Updates

### WiFi OTA (Over-the-Air Updates)
```cpp
#include <WiFi.h>
#include <ArduinoOTA.h>

void setup() {
  WiFi.begin(ssid, password);
  
  ArduinoOTA.setHostname("project-ai-pipboy");
  ArduinoOTA.setPassword("secure_ota_password");
  
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Update Starting...");
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA Update Complete");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
}
```

---

**Document Version:** 1.0.0  
**Platform Revision:** ESP32-S3 (v1.1), ESP32-C6 (v1.0), ESP32 (legacy)  
**Last Review:** 2026-02-22
