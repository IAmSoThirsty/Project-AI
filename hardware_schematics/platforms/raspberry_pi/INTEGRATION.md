# Raspberry Pi Platform Integration Guide

**Platform:** Raspberry Pi (Models 5, 4, Zero 2W)  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready

---

## Overview

This guide provides comprehensive integration strategies for deploying Project-AI Pip-Boy variants on Raspberry Pi single-board computers. Covers hardware interfacing, performance optimization, power management, and deployment configurations for Pi 5 (high-performance), Pi 4 (standard), and Pi Zero 2W (ultra-portable) platforms.

---

## Supported Models

### Raspberry Pi 5 (Recommended)
- **CPU:** Broadcom BCM2712, Quad-core ARM Cortex-A76 @ 2.4GHz
- **GPU:** VideoCore VII, OpenGL ES 3.1, Vulkan 1.2
- **RAM:** 4GB or 8GB LPDDR4X-4267
- **Storage:** MicroSD + M.2 HAT (NVMe SSD support via PCIe 2.0 x1)
- **Power:** 5V 5A (25W) via USB-C PD
- **Features:** 2x MIPI CSI camera, 2x MIPI DSI display, PCIe 2.0
- **Performance:** ~3.5x faster than Pi 4 (multi-threaded)
- **Best For:** Full-featured variants (Engineer, Scientist, Military)

### Raspberry Pi 4 (Standard)
- **CPU:** Broadcom BCM2711, Quad-core ARM Cortex-A72 @ 1.8GHz
- **GPU:** VideoCore VI, OpenGL ES 3.0
- **RAM:** 2GB, 4GB, or 8GB LPDDR4-3200
- **Storage:** MicroSD (UHS-I)
- **Power:** 5V 3A (15W) via USB-C
- **Features:** 2x micro-HDMI, 4x USB 3.0/2.0, Gigabit Ethernet, WiFi 5, BT 5.0
- **Performance:** Baseline for standard deployments
- **Best For:** Most variants (Student, Journalist, Researcher, Lawyer)

### Raspberry Pi Zero 2 W (Ultra-Portable)
- **CPU:** Broadcom RP3A0, Quad-core ARM Cortex-A53 @ 1GHz
- **GPU:** VideoCore IV, OpenGL ES 2.0
- **RAM:** 512MB LPDDR2
- **Storage:** MicroSD (Class 10 minimum)
- **Power:** 5V 1A (5W) via micro-USB or GPIO
- **Features:** Mini-HDMI, micro-USB OTG, WiFi 4, BT 4.2
- **Performance:** 5x faster than original Pi Zero
- **Best For:** Low-power variants (Student, basic Enterprise)

---

## Hardware Integration

### 1. Display Integration

#### 3.5" AMOLED Touch Display
**Recommended:** Waveshare 3.5inch AMOLED (C) 800x480 SPI

```bash
# Install drivers
git clone https://github.com/waveshare/AMOLED_SPI_Module.git
cd AMOLED_SPI_Module
sudo ./install.sh

# Configure /boot/config.txt
dtoverlay=piscreen,rotate=90,speed=40000000,fps=60

# Test display
sudo fbcp &
```

**Pin Connections (GPIO):**
```
AMOLED Module    Raspberry Pi
VCC     -------> 3.3V (Pin 1)
GND     -------> GND (Pin 6)
DIN     -------> MOSI (Pin 19, GPIO 10)
CLK     -------> SCLK (Pin 23, GPIO 11)
CS      -------> CE0 (Pin 24, GPIO 8)
DC      -------> GPIO 25 (Pin 22)
RST     -------> GPIO 27 (Pin 13)
BL      -------> GPIO 18 (Pin 12, PWM)
```

**Performance Optimizations:**
- SPI Clock: 40MHz (Pi 4/5), 32MHz (Pi Zero 2W)
- DMA: Enable for reduced CPU usage
- Frame Buffer: Use `fbcp-ili9341` for 60fps refresh
- Power Consumption: 0.5-0.8W (typical), 1.2W (max brightness)

### 2. Sensor Integration

#### I2C Sensors (All Variants)
**Base Configuration (`/boot/config.txt`):**
```ini
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=400000  # 400kHz Fast Mode
```

**Common I2C Devices:**
| Address | Device | Variant | Purpose |
|---------|--------|---------|---------|
| 0x29 | TSL2591 | All | Ambient light sensor |
| 0x40 | SHT40 | Scientist, Geologist | Temperature/humidity |
| 0x48 | ADS1115 | Engineer | 16-bit ADC (multimeter) |
| 0x62 | SCD41 | Scientist | CO₂ sensor |
| 0x68 | MPU6050 | All | 6-axis IMU |
| 0x76 | BMP390 | All | Barometric pressure |
| 0x77 | BMP390 (alt) | All | Barometric pressure (alt address) |

**Python Example (BMP390):**
```python
import board
import adafruit_bmp3xx

i2c = board.I2C()
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

print(f"Temperature: {bmp.temperature:.2f} °C")
print(f"Pressure: {bmp.pressure:.2f} hPa")
print(f"Altitude: {bmp.altitude:.2f} m")
```

#### SPI Sensors (High-Speed Devices)
**Enable SPI (`/boot/config.txt`):**
```ini
dtparam=spi=on
```

**SPI Devices:**
- **Engineer:** AD9833 (DDS function generator), ADS1263 (24-bit ADC)
- **Scientist:** C12880MA (spectrometer), MAX31856 (thermocouple)
- **Military:** SAASM GPS (classified interface)

### 3. Camera Integration

#### MIPI CSI Camera (Pi 5 supports 2 cameras)
**Recommended:** Raspberry Pi Camera Module 3 (12MP, autofocus)

```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable

# Test camera
libcamera-hello --timeout 5000

# Capture photo
libcamera-still -o test.jpg

# Record video (1080p @ 30fps)
libcamera-vid -t 60000 -o video.h264 --width 1920 --height 1080 --framerate 30
```

**Body Camera Integration (Law Enforcement variant):**
```python
from picamera2 import Picamera2
from datetime import datetime
import hashlib

picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1920, 1080), "format": "RGB888"},
    encode="high"
)
picam2.configure(config)

# Start recording with timestamp
timestamp = datetime.utcnow().isoformat()
filename = f"bodycam_{timestamp}.h264"
picam2.start_recording(filename)

# ... record for duration ...

picam2.stop_recording()

# Generate SHA-256 hash for chain of custody
with open(filename, 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"Evidence Hash: {file_hash}")
```

### 4. GPS Module Integration

#### UART GPS (u-blox NEO-M8N or ZED-F9P)
**Wiring:**
```
GPS Module    Raspberry Pi
VCC   ------> 3.3V (Pin 1)
GND   ------> GND (Pin 6)
TX    ------> RX (Pin 10, GPIO 15)
RX    ------> TX (Pin 8, GPIO 14)
```

**Configure Serial (`/boot/config.txt`):**
```ini
enable_uart=1
dtoverlay=disable-bt  # Disable Bluetooth (uses same UART)
```

**Python Example (gpsd):**
```bash
# Install gpsd
sudo apt install gpsd gpsd-clients python3-gps

# Configure gpsd
sudo systemctl stop gpsd
sudo gpsd /dev/serial0 -F /var/run/gpsd.sock
sudo systemctl start gpsd
```

```python
from gps3 import gps3

gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()

for new_data in gps_socket:
    if new_data:
        data_stream.unpack(new_data)
        print(f"Lat: {data_stream.TPV['lat']}, Lon: {data_stream.TPV['lon']}")
        print(f"Altitude: {data_stream.TPV['alt']} m")
        print(f"Speed: {data_stream.TPV['speed']} m/s")
```

### 5. Audio Integration

#### Professional Audio Codec (Journalist variant)
**Recommended:** HiFiBerry DAC+ ADC Pro (192kHz/24-bit)

```bash
# Install HiFiBerry drivers
curl -sL https://install.hifiberry.com/install.sh | bash

# Configure /boot/config.txt
dtoverlay=hifiberry-dacplusadcpro

# Test audio
arecord -D plughw:0,0 -f S24_LE -r 48000 -c 2 test.wav
aplay -D plughw:0,0 test.wav
```

**ALSA Configuration (`/etc/asound.conf`):**
```
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "output"
  }
  capture.pcm {
    type plug
    slave.pcm "input"
  }
}

pcm.output {
  type hw
  card 0
}

pcm.input {
  type hw
  card 0
}
```

---

## Power Management

### Power Consumption Analysis

#### Raspberry Pi 5 (8GB)
| State | Current @ 5V | Power | Notes |
|-------|-------------|-------|-------|
| Idle (Desktop) | 1.5A | 7.5W | Display off, WiFi on |
| Light Load | 2.5A | 12.5W | Web browsing, sensors |
| Heavy Load | 4.5A | 22.5W | 4K video, AI inference |
| Max (Stress) | 5.0A | 25W | All cores 100% + GPU |

#### Raspberry Pi 4 (4GB)
| State | Current @ 5V | Power | Notes |
|-------|-------------|-------|-------|
| Idle | 0.7A | 3.5W | Display off, WiFi on |
| Light Load | 1.2A | 6W | Web browsing |
| Heavy Load | 2.5A | 12.5W | Video playback |
| Max | 3.0A | 15W | All cores 100% |

#### Raspberry Pi Zero 2W
| State | Current @ 5V | Power | Notes |
|-------|-------------|-------|-------|
| Idle | 0.15A | 0.75W | WiFi on, no display |
| Light Load | 0.3A | 1.5W | Basic tasks |
| Heavy Load | 0.6A | 3W | Video playback |
| Max | 1.0A | 5W | All cores 100% |

### Battery Runtime Calculations

**3000mAh Li-Po Battery (11.1Wh)**
- **Pi 5:** 0.5-1.5 hours (heavy use)
- **Pi 4:** 1-3 hours (standard use)
- **Pi Zero 2W:** 3-15 hours (light use)

**6000mAh Battery (22.2Wh)**
- **Pi 5:** 1-3 hours
- **Pi 4:** 2-6 hours
- **Pi Zero 2W:** 6-30 hours

### Power Optimization Techniques

```bash
# Disable HDMI (saves 25mA on Pi 4)
/usr/bin/tvservice -o

# Disable WiFi (saves 50mA)
sudo ifconfig wlan0 down

# Disable Bluetooth (saves 30mA)
sudo systemctl disable bluetooth

# Reduce GPU memory (in /boot/config.txt)
gpu_mem=16  # Minimum for console-only

# CPU frequency scaling
sudo cpufreq-set -g powersave

# Undervolt CPU (CAUTION: May cause instability)
# Add to /boot/config.txt
over_voltage=-2  # Reduce voltage by 50mV
```

---

## Operating System Configuration

### Recommended OS Images

#### Raspberry Pi OS Lite (64-bit)
**Best for:** Production deployments (headless, minimal overhead)
```bash
# Download image
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/latest.zip

# Flash to microSD (Linux)
sudo dd if=2024-07-04-raspios-bookworm-arm64-lite.img of=/dev/sdX bs=4M status=progress

# First boot configuration
sudo raspi-config
# - Enable SSH, I2C, SPI, Camera
# - Set locale, timezone, keyboard
# - Expand filesystem
```

#### Ubuntu Server 23.10 (ARM64)
**Best for:** Containerized deployments (Docker, Kubernetes)
```bash
# Download Ubuntu Server
wget https://cdimage.ubuntu.com/releases/23.10/release/ubuntu-23.10-preinstalled-server-arm64+raspi.img.xz

# Flash to microSD
xzcat ubuntu-23.10-preinstalled-server-arm64+raspi.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# First boot (cloud-init)
# - Default user: ubuntu, password: ubuntu (forced change on first login)
```

### System Optimization

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3-pip python3-venv git vim htop

# Create virtual environment for Project-AI
python3 -m venv ~/project-ai-env
source ~/project-ai-env/bin/activate

# Install Project-AI dependencies
pip install -r /path/to/project-ai/requirements.txt

# Enable swap (recommended for 2GB or less RAM)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## AI Model Deployment

### TensorFlow Lite (Optimized for ARM)

```bash
# Install TensorFlow Lite runtime
pip install tflite-runtime

# Download optimized models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/mobilenet_v2_1.0_224_quant.tflite

# Example inference (image classification)
```

```python
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

# Load model
interpreter = tflite.Interpreter(model_path="mobilenet_v2_1.0_224_quant.tflite")
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load and preprocess image
img = Image.open("test.jpg").resize((224, 224))
input_data = np.expand_dims(np.array(img, dtype=np.uint8), axis=0)

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

print(f"Predictions: {output_data}")
```

**Performance Benchmarks (MobileNetV2, 224x224):**
- **Pi 5:** 15ms/inference (66 fps)
- **Pi 4:** 45ms/inference (22 fps)
- **Pi Zero 2W:** 180ms/inference (5.5 fps)

### ONNX Runtime (Cross-Platform)

```bash
# Install ONNX Runtime (ARM64)
pip install onnxruntime

# Example inference
```

```python
import onnxruntime as ort
import numpy as np

# Load model
session = ort.InferenceSession("model.onnx")

# Run inference
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)

result = session.run([output_name], {input_name: input_data})
print(f"Output: {result}")
```

---

## Deployment Configurations

### Configuration 1: Pi 5 + Engineer Variant
**Components:**
- Raspberry Pi 5 (8GB)
- Waveshare 3.5" AMOLED touch display
- ADS1263 24-bit ADC (multimeter)
- AD9042 oscilloscope frontend
- iCE40 FPGA (logic analyzer)
- 6000mAh battery (3 hours runtime)

**Total Power:** 15-20W (typical use)  
**Cost:** $485 (Pi 5 $80 + base $110 + Engineer components $153 + battery $35 + case $25 + misc $82)

### Configuration 2: Pi 4 + Scientist Variant
**Components:**
- Raspberry Pi 4 (4GB)
- C12880MA spectrometer
- ADS1220 pH meter ADC
- Environmental sensors (SHT40, BMP390, SCD41, SGP40)
- 4x MAX31856 thermocouple inputs
- 3000mAh battery (6 hours runtime)

**Total Power:** 8-12W (typical use)  
**Cost:** $497 (Pi 4 $55 + base $110 + Scientist components $302 + misc $30)

### Configuration 3: Pi Zero 2W + Student Variant
**Components:**
- Raspberry Pi Zero 2W
- 2.8" resistive touch display (SPI)
- Basic sensors (IMU, environmental)
- USB-A adapter (OTG)
- 1500mAh battery (12 hours runtime)

**Total Power:** 2-4W (typical use)  
**Cost:** $145 (Pi Zero $15 + base $85 + display $25 + battery $10 + misc $10)

---

## Performance Optimization

### GPU Acceleration

```bash
# Enable VideoCore GPU (Pi 4/5)
# Add to /boot/config.txt
gpu_mem=256  # Allocate 256MB to GPU

# Install OpenGL ES libraries
sudo apt install libegl1-mesa-dev libgles2-mesa-dev

# Test GPU rendering
glxgears  # Should show 60fps+
```

### Multi-Threading

```python
import concurrent.futures
import time

def sensor_read(sensor_id):
    # Simulate sensor reading
    time.sleep(0.1)
    return f"Sensor {sensor_id}: {random.randint(0, 100)}"

# Parallel sensor reads (4 cores = 4 simultaneous reads)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(sensor_read, i) for i in range(16)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(results)
```

### Memory Optimization

```python
# Use generators instead of lists (lower memory)
def sensor_stream():
    while True:
        yield read_sensor()

# Process one at a time (constant memory)
for reading in sensor_stream():
    process(reading)
```

---

## Appendix A: Pin Allocation Table

### GPIO Pinout (Raspberry Pi 5/4, 40-pin header)
| Pin | GPIO | Function | Variant | Device |
|-----|------|----------|---------|--------|
| 1 | 3.3V | Power | All | Sensors |
| 2 | 5V | Power | All | Display |
| 3 | GPIO 2 | I2C SDA | All | I2C sensors |
| 5 | GPIO 3 | I2C SCL | All | I2C sensors |
| 7 | GPIO 4 | Digital I/O | Engineer | Logic analyzer CH0 |
| 8 | GPIO 14 | UART TX | All | GPS TX |
| 10 | GPIO 15 | UART RX | All | GPS RX |
| 11 | GPIO 17 | Digital I/O | Engineer | Trigger output |
| 12 | GPIO 18 | PWM 0 | All | Display backlight |
| 13 | GPIO 27 | Digital I/O | All | Display reset |
| 15 | GPIO 22 | Digital I/O | Engineer | Function gen sync |
| 19 | GPIO 10 | SPI MOSI | All | Display SPI |
| 21 | GPIO 9 | SPI MISO | Scientist | Spectrometer |
| 23 | GPIO 11 | SPI SCLK | All | Display/SPI |
| 24 | GPIO 8 | SPI CE0 | All | Display CS |
| 26 | GPIO 7 | SPI CE1 | Scientist | Spectrometer CS |

---

## Appendix B: Troubleshooting

### Issue: Display not working
```bash
# Check SPI enabled
lsmod | grep spi

# Test SPI communication
sudo apt install python3-spidev
python3 -c "import spidev; spi = spidev.SpiDev(); spi.open(0,0); print('SPI OK')"

# Check GPIO permissions
sudo usermod -a -G spi,gpio $USER
```

### Issue: I2C devices not detected
```bash
# Scan I2C bus
sudo i2cdetect -y 1

# Check I2C speed (slow down if errors)
# In /boot/config.txt:
dtparam=i2c_arm_baudrate=100000  # Reduce to 100kHz

# Enable I2C bus 0 (if needed)
dtparam=i2c_vc=on
```

### Issue: GPS not getting fix
```bash
# Check GPS signal
gpsmon /dev/serial0

# Verify antenna connection (active antenna needs 3.3V)
# Check for "Antenna: OK" in gpsmon

# Outdoor test (GPS requires clear sky view)
# Wait 5-10 minutes for cold start
```

---

**Document Version:** 1.0.0  
**Platform Revision:** Pi 5 (RP1), Pi 4 (BCM2711), Pi Zero 2W (RP3A0)  
**Last Review:** 2026-02-22
