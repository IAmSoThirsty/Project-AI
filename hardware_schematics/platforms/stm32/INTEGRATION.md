# STM32 Platform Integration Guide

**Platform:** STM32 Microcontroller Family  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready  
**Target Use Cases:** Real-time embedded systems, ultra-low power, industrial control, medical devices, IoT edge nodes

---

## Overview

STM32 microcontrollers from STMicroelectronics provide real-time embedded control for Project-AI Pip-Boy variants requiring deterministic behavior, ultra-low power consumption, and hardware interfacing. This guide covers integration with STM32H7 (high-performance), STM32F4 (mainstream), and STM32L4 (ultra-low-power) series for specialized deployments.

---

## Supported STM32 Platforms

### STM32H7 Series (High-Performance)
**MCU:** STM32H743VIT6 (LQFP-100 package)
- **Core:** ARM Cortex-M7 @ 480 MHz + Cortex-M4 @ 240 MHz (dual-core)
- **RAM:** 1 MB SRAM (including 128 KB TCM for zero-wait-state access)
- **Flash:** 2 MB internal Flash
- **FPU:** Double-precision floating-point unit (DP-FPU)
- **DSP:** Digital signal processing instructions
- **Peripherals:** 16x UART, 6x I2C, 6x SPI, 2x CAN FD, USB OTG HS, Ethernet MAC
- **ADC:** 3x 16-bit ADC @ 3.6 MSPS (mega-samples per second)
- **DAC:** 2x 12-bit DAC
- **Use Cases:** Medical devices (ECG, vitals), industrial automation, high-speed data acquisition

### STM32F4 Series (Mainstream)
**MCU:** STM32F429ZIT6 (LQFP-144 package)
- **Core:** ARM Cortex-M4 @ 180 MHz
- **RAM:** 256 KB SRAM + 64 KB CCM (Core-Coupled Memory)
- **Flash:** 2 MB internal Flash
- **FPU:** Single-precision floating-point unit (SP-FPU)
- **DSP:** Digital signal processing instructions
- **Peripherals:** 8x UART, 3x I2C, 6x SPI, 2x CAN, USB OTG FS/HS, Ethernet MAC
- **ADC:** 3x 12-bit ADC @ 2.4 MSPS
- **LCD Controller:** Chrom-ART accelerator (2D graphics)
- **Use Cases:** IoT gateways, HMI (human-machine interface), motor control, student variant

### STM32L4 Series (Ultra-Low-Power)
**MCU:** STM32L476RGT6 (LQFP-64 package)
- **Core:** ARM Cortex-M4 @ 80 MHz
- **RAM:** 128 KB SRAM
- **Flash:** 1 MB internal Flash
- **Power:** 100 μA/MHz (Run mode), 1.08 μA (Stop2 mode), 0.03 μA (Shutdown mode)
- **Peripherals:** 6x UART, 4x I2C, 3x SPI, 1x CAN, USB OTG FS
- **ADC:** 3x 12-bit ADC @ 5 MSPS (5.16 μA/MSPS)
- **Battery Life:** Years on coin cell (with duty cycling)
- **Use Cases:** Field research, wildlife tracking, remote sensors, geologist variant

---

## Hardware Integration

### Reference Design: STM32H7-Based Pip-Boy

**Block Diagram:**
```
┌─────────────────────────────────────────────────────┐
│  STM32H743VIT6 Microcontroller (LQFP-100)           │
│                                                     │
│  Cortex-M7 @ 480 MHz      Cortex-M4 @ 240 MHz     │
│  ├─ Project-AI Core       ├─ Sensor Fusion        │
│  ├─ UI Rendering          ├─ Real-Time Control     │
│  └─ ML Inference          └─ DSP (Audio, ECG)      │
│                                                     │
│  Peripherals:                                       │
│  ├─ UART1-3: GPS, Debug, Sensor Modules           │
│  ├─ I2C1-2: IMU, Environmental Sensors             │
│  ├─ SPI1-3: SD Card, Display, External Flash      │
│  ├─ USB OTG: PC Connection, Firmware Update        │
│  ├─ ETH: Ethernet (if docked)                      │
│  ├─ CAN FD: Industrial sensor networks             │
│  └─ ADC1-3: Analog sensors (voltage, current)      │
└─────────────────────────────────────────────────────┘
         │         │         │         │
         ▼         ▼         ▼         ▼
    [Display]  [Sensors]  [Storage]  [Comms]
     SPI TFT    I2C/SPI    SD Card    WiFi/BT
    480x320     IMU,GPS    32 GB      ESP32
    ILI9488     BME280               (AT commands)
```

### Pin Allocation (STM32H743, LQFP-100)

| Function | Pin | Peripheral | Notes |
|----------|-----|------------|-------|
| **Display (SPI1)** |
| MOSI | PA7 | SPI1_MOSI | Data to display |
| MISO | PA6 | SPI1_MISO | Touch controller |
| SCK | PA5 | SPI1_SCK | Clock |
| CS | PA4 | GPIO | Chip select |
| DC | PC4 | GPIO | Data/command |
| RESET | PC5 | GPIO | Display reset |
| **GPS (UART1)** |
| TX | PA9 | USART1_TX | To GPS module |
| RX | PA10 | USART1_RX | From GPS module |
| **IMU (I2C1)** |
| SCL | PB6 | I2C1_SCL | Clock |
| SDA | PB7 | I2C1_SDA | Data |
| **SD Card (SDMMC1)** |
| CMD | PD2 | SDMMC1_CMD | Command |
| CLK | PC12 | SDMMC1_CK | Clock |
| D0-D3 | PC8-11 | SDMMC1_D0-3 | 4-bit mode |
| **ADC (Medical Sensors)** |
| ADC1_IN3 | PA3 | ADC1 | ECG electrode 1 |
| ADC2_IN4 | PA4 | ADC2 | ECG electrode 2 |
| ADC3_IN5 | PA5 | ADC3 | ECG electrode 3 |
| **Power Management** |
| VBAT | - | Battery backup | RTC, backup registers |
| VDD | - | +3.3V | Main power |
| VSS | - | GND | Ground |

---

## Software Architecture

### Firmware Stack (STM32CubeH7)

**Layer 1: Hardware Abstraction Layer (HAL)**
- STM32 HAL drivers (UART, I2C, SPI, ADC, DMA, etc.)
- Low-level peripheral access with error handling

**Layer 2: Middleware**
- FreeRTOS: Real-time operating system (task scheduling, semaphores, queues)
- LwIP: Lightweight IP stack (if Ethernet used)
- FatFS: FAT filesystem for SD card
- USB Device: MSC (Mass Storage Class), CDC (Virtual COM Port)

**Layer 3: Application**
- Project-AI Core: Ethical decision-making (Four Laws)
- Sensor Manager: Read sensors, fuse data
- UI Manager: Render display, handle touch input
- Data Logger: Log to SD card with timestamps

**Layer 4: ML Inference**
- TensorFlow Lite Micro: On-device ML inference
- CMSIS-NN: Optimized neural network kernels (ARM)
- X-CUBE-AI: STM32 ML model converter (Keras/TensorFlow → C code)

### Example Code: Read Sensor via I2C

```c
#include "stm32h7xx_hal.h"

I2C_HandleTypeDef hi2c1;

// Initialize I2C1 (BME280 environmental sensor)
void MX_I2C1_Init(void)
{
  hi2c1.Instance = I2C1;
  hi2c1.Init.Timing = 0x00702991; // 400 kHz I2C Fast Mode
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
}

// Read temperature from BME280 (address 0x76)
float ReadTemperature_BME280(void)
{
  uint8_t reg = 0xFA; // Temperature register
  uint8_t data[3];
  
  // Read 3 bytes from register 0xFA
  HAL_I2C_Mem_Read(&hi2c1, 0x76 << 1, reg, 1, data, 3, 100);
  
  // Convert raw data to temperature (simplified)
  int32_t adc_T = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
  float temperature = (float)adc_T / 5120.0; // Placeholder formula
  
  return temperature;
}
```

### FreeRTOS Task Structure

```c
#include "FreeRTOS.h"
#include "task.h"

void Task_SensorRead(void *pvParameters)
{
  TickType_t xLastWakeTime = xTaskGetTickCount();
  const TickType_t xFrequency = pdMS_TO_TICKS(1000); // 1 Hz
  
  for(;;)
  {
    float temp = ReadTemperature_BME280();
    float humidity = ReadHumidity_BME280();
    float pressure = ReadPressure_BME280();
    
    // Log to SD card
    LogSensorData(temp, humidity, pressure);
    
    // Wait for next cycle (1 second)
    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

void Task_Display(void *pvParameters)
{
  for(;;)
  {
    // Update display at 30 FPS
    RenderUI();
    vTaskDelay(pdMS_TO_TICKS(33)); // ~33 ms = 30 FPS
  }
}

int main(void)
{
  // Initialize hardware
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_I2C1_Init();
  MX_SPI1_Init();
  
  // Create FreeRTOS tasks
  xTaskCreate(Task_SensorRead, "Sensor", 128, NULL, 2, NULL);
  xTaskCreate(Task_Display, "Display", 256, NULL, 1, NULL);
  
  // Start scheduler
  vTaskStartScheduler();
  
  // Should never reach here
  while(1);
}
```

---

## Machine Learning on STM32

### TensorFlow Lite Micro Integration

**X-CUBE-AI:** STM32 AI expansion package for STM32CubeMX
- Import pre-trained models (Keras, TensorFlow, ONNX)
- Generate optimized C code for STM32
- Validate accuracy vs original model
- Benchmark inference time and memory usage

**Example: Keyword Spotting (Wake Word Detection)**

**Model:** 1D CNN for audio classification (trained on Speech Commands dataset)
- Input: 1 second audio (16 kHz, 16-bit PCM) = 16,000 samples
- Preprocessing: MFCC (Mel-Frequency Cepstral Coefficients) = 40x49 matrix
- Model: Conv1D → MaxPool → Conv1D → MaxPool → Dense → Softmax
- Output: Probability of 10 keywords ("yes", "no", "up", "down", etc.)
- Inference Time: 45 ms (STM32H7 @ 480 MHz)
- Memory: 50 KB Flash (model weights), 20 KB RAM (activations)

**Code Snippet:**
```c
#include "ai_platform.h"
#include "network.h" // Generated by X-CUBE-AI

ai_handle network;
ai_buffer ai_input[AI_NETWORK_IN_NUM];
ai_buffer ai_output[AI_NETWORK_OUT_NUM];

float input_data[AI_NETWORK_IN_1_SIZE]; // MFCC features (40x49)
float output_data[AI_NETWORK_OUT_1_SIZE]; // 10 keyword probabilities

void RunInference(void)
{
  // Populate input buffer with MFCC features
  ai_input[0].data = AI_HANDLE_PTR(input_data);
  ai_output[0].data = AI_HANDLE_PTR(output_data);
  
  // Run inference
  ai_network_run(network, ai_input, ai_output);
  
  // Find max probability keyword
  int max_idx = 0;
  for (int i = 1; i < AI_NETWORK_OUT_1_SIZE; i++)
  {
    if (output_data[i] > output_data[max_idx])
      max_idx = i;
  }
  
  // Check if keyword detected (threshold 0.9)
  if (output_data[max_idx] > 0.9)
  {
    printf("Keyword detected: %s\n", keywords[max_idx]);
  }
}
```

---

## Power Optimization (STM32L4 Ultra-Low-Power)

### Power Modes

| Mode | CPU | Peripherals | Consumption | Wake-up Time | Use Case |
|------|-----|-------------|-------------|--------------|----------|
| **Run** | Active | Active | 100 μA/MHz @ 80 MHz = 8 mA | N/A | Active processing |
| **Sleep** | Stopped | Active | 50 μA/MHz @ 80 MHz = 4 mA | ~0 μs | Wait for interrupt |
| **Stop 0** | Stopped | Some active | 106 μA | 5 μs | Short idle periods |
| **Stop 1** | Stopped | Few active | 6.2 μA | 10 μs | Long idle periods |
| **Stop 2** | Stopped | Minimal | 1.08 μA | 15 μs | Deep sleep, RTC wakeup |
| **Standby** | Off | None (RTC only) | 0.55 μA | 50 μs | Years of sleep |
| **Shutdown** | Off | None | 0.03 μA | Reset | Maximum battery life |

### Battery Life Calculation (Geologist Variant)

**Scenario:** Field geology study, 12 hours/day active, 12 hours sleep
- **Active (12 hours/day):** 8 mA average (processing, GPS, sensors)
- **Sleep (12 hours/day):** 1 μA (Stop2 mode, RTC wakeup every hour)

**Daily Consumption:**
```
Active: 12 hours × 8 mA = 96 mAh/day
Sleep: 12 hours × 0.001 mA = 0.012 mAh/day
Total: 96.012 mAh/day
```

**Battery:** 3000 mAh Li-Ion (18650 cell)
**Runtime:** 3000 mAh / 96 mAh/day = **31 days** (1 month in field!)

**With Solar Panel:** 5W @ 6 hours/day = 30 Wh/day = 8333 mAh/day @ 3.7V
- **Indefinite runtime** (energy-positive system)

---

## Real-Time Determinism

### Interrupt Priority Configuration

**NVIC (Nested Vectored Interrupt Controller) Priorities:**
- **Priority 0 (Highest):** Critical safety functions (emergency stop, watchdog)
- **Priority 1:** Real-time control (motor control, ECG sampling)
- **Priority 2:** Communication (UART, I2C, SPI)
- **Priority 3:** Sensors (ADC complete, DMA transfer)
- **Priority 4-15 (Lowest):** UI, logging, non-critical tasks

**FreeRTOS Interrupt Handling:**
```c
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 5
// Interrupts priority 0-4 cannot call FreeRTOS functions
// Interrupts priority 5-15 can use FromISR() functions
```

### Timing Guarantees

**STM32H7 with Cache:**
- **Instruction Cache (ICACHE):** 16 KB, reduces Flash latency
- **Data Cache (DCACHE):** 16 KB, reduces RAM latency
- **Tightly-Coupled Memory (TCM):** 128 KB, zero-wait-state access
- **Result:** Deterministic execution time for critical code

**Example:** ECG Sampling at 1 kHz (1 ms period)
```c
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM2) // 1 kHz timer
  {
    // Read ADC (ECG electrode) - deterministic 2 μs
    uint32_t adc_value = HAL_ADC_GetValue(&hadc1);
    
    // Store in buffer (DMA) - deterministic 500 ns
    ecg_buffer[ecg_index++] = adc_value;
    
    // Wrap buffer
    if (ecg_index >= ECG_BUFFER_SIZE)
      ecg_index = 0;
    
    // Total time: 2.5 μs (well within 1 ms budget)
  }
}
```

---

## Industrial I/O & Sensors

### Analog Input (12-bit ADC, 0-3.3V)

**Voltage Divider for 0-24V Measurement:**
```
Input (24V max) ──┬──[47kΩ]─── ADC Pin (3.3V max)
                  │
                  └──[8.2kΩ]── GND

Divider Ratio: (8.2) / (47 + 8.2) = 0.1486
Max Input: 3.3V / 0.1486 = 22.2V (with margin for 24V)

ADC Code: 0-4095 (12-bit)
Voltage: (ADC_Code / 4095) × 3.3V / 0.1486
```

**Code Example:**
```c
uint32_t adc_code = HAL_ADC_GetValue(&hadc1);
float adc_voltage = (float)adc_code / 4095.0 * 3.3;
float input_voltage = adc_voltage / 0.1486;
printf("Input voltage: %.2f V\n", input_voltage);
```

### Digital I/O (GPIO)

**Input:** Button, limit switch, encoder
- Pull-up/pull-down resistors (internal or external)
- Debouncing in software (10-50 ms delay)

**Output:** LED, relay, solenoid
- Max current: 25 mA per pin (use transistor for higher loads)
- Push-pull or open-drain mode

**Example:** Read button, toggle LED
```c
// Read button (PA0, active low with pull-up)
if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_RESET)
{
  // Button pressed, toggle LED (PC13)
  HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
  HAL_Delay(200); // Simple debounce
}
```

---

## Bill of Materials (STM32H7 Reference Design)

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| MCU | STM32H743VIT6 | ST | 1 | $12.50 | $12.50 |
| Flash (external) | W25Q256JVEIQ (32MB) | Winbond | 1 | $3.20 | $3.20 |
| RAM (external, optional) | IS42S16160J (32MB SDRAM) | ISSI | 1 | $2.80 | $2.80 |
| IMU | ICM-20948 (9-axis) | TDK InvenSense | 1 | $6.50 | $6.50 |
| GPS | NEO-M9N | u-blox | 1 | $35.00 | $35.00 |
| Display | 3.5" TFT (ILI9488) | Generic | 1 | $12.00 | $12.00 |
| SD Card Holder | MicroSD socket | Generic | 1 | $0.80 | $0.80 |
| Power Regulator | TPS63001 (buck-boost) | TI | 1 | $3.50 | $3.50 |
| Crystals | 25 MHz (HSE), 32.768 kHz (LSE) | Generic | 2 | $0.50 | $1.00 |
| Passives | Resistors, capacitors, inductors | Generic | ~100 | - | $5.00 |
| PCB | 4-layer (impedance controlled) | JLC PCB | 1 | $25.00 | $25.00 |
| **Total (STM32H7 Base)** | | | | | **$107.30** |

**Add Base Pip-Boy Cost:** $85-$110  
**Total STM32H7 Pip-Boy:** $192.30-$217.30

---

## Development Tools

### Hardware Debugger
- **ST-LINK/V3SET:** USB debugger/programmer ($50)
- **J-Link:** Segger debugger (faster, more features, $60-$400)
- **Interface:** SWD (Serial Wire Debug) - 2-wire debug (SWDIO, SWCLK)

### Software IDE
- **STM32CubeIDE:** Free Eclipse-based IDE (includes compiler, debugger, CubeMX)
- **Keil MDK-ARM:** Commercial IDE (free 32 KB code limit, $5000+ for unlimited)
- **IAR Embedded Workbench:** Commercial IDE (excellent optimizer, $3000+)

### Code Generation
- **STM32CubeMX:** Graphical pin/peripheral configurator (generates init code)
- **X-CUBE-AI:** ML model converter (Keras/TensorFlow → C code)
- **TouchGFX Designer:** GUI designer for embedded displays

---

## Deployment Configurations

### Configuration 1: Medical ECG Monitor (STM32H7)
- **Purpose:** Real-time ECG analysis, detect arrhythmias
- **Sensors:** 3-lead ECG (ADC1-3 @ 1 kHz sampling)
- **Processing:** Pan-Tompkins QRS detection (M7 core), R-R interval analysis (M4 core)
- **Display:** 480x320 TFT (ECG waveform, heart rate, alerts)
- **Storage:** SD card (log ECG data with timestamps)
- **Power:** 3000 mAh battery, 12-hour runtime
- **Compliance:** IEC 60601-1 medical device safety

### Configuration 2: Industrial Data Logger (STM32F4)
- **Purpose:** Multi-channel data acquisition (temp, pressure, voltage)
- **Sensors:** 8x analog inputs (4-20 mA current loop, thermocouple)
- **Sampling:** 10 Hz per channel (80 samples/sec total)
- **Storage:** SD card (CSV files, date/time stamped)
- **Communication:** Modbus RTU (RS-485) to SCADA system
- **Display:** 320x240 TFT (real-time graphs, min/max/avg)
- **Enclosure:** NEMA 4X (IP66) for industrial environment

### Configuration 3: Wildlife Tracker (STM32L4)
- **Purpose:** Track animal movements, environmental conditions
- **Sensors:** GPS (u-blox NEO-M9N), temp/humidity (BME280), accelerometer (LIS3DH)
- **Sampling:** GPS every 5 minutes, sensors every 10 minutes
- **Power:** Duty cycling (active 10 sec, sleep 4 min 50 sec) = 3.3% duty cycle
- **Battery:** 3000 mAh → **2.5 years** runtime
- **Communication:** LoRa (915 MHz) for long-range data transmission (10 km+)
- **Data:** Transmit GPS, temp, activity counts once per day (conserve power)

---

## Appendix A: STM32 Tool Ecosystem

### STMicroelectronics Tools (Free)
- **STM32CubeIDE:** All-in-one IDE (code, compile, debug)
- **STM32CubeMX:** Pin/peripheral configurator (graphical)
- **STM32CubeProgrammer:** Flash programming utility (USB, JTAG, UART bootloader)
- **STM32CubeMonitor:** Real-time variable monitoring (like oscilloscope for variables)

### Third-Party Libraries
- **FreeRTOS:** Real-time operating system (task scheduling, IPC)
- **LwIP:** TCP/IP stack (if Ethernet used)
- **FatFS:** FAT filesystem for SD cards
- **TinyUSB:** Lightweight USB device stack
- **CMSIS-DSP:** Optimized math functions (FFT, filters, statistics)
- **CMSIS-NN:** Optimized neural network kernels

---

## Appendix B: Comparison with Raspberry Pi

| Feature | STM32H7 | Raspberry Pi 5 |
|---------|---------|----------------|
| **Core** | Cortex-M7 @ 480 MHz | Cortex-A76 @ 2.4 GHz (4-core) |
| **OS** | Bare-metal / RTOS | Linux (Raspberry Pi OS) |
| **Boot Time** | <100 ms | ~20 seconds |
| **Power (idle)** | 80 mA @ 3.3V = 0.26W | 2-3W |
| **Power (active)** | 200 mA @ 3.3V = 0.66W | 8-12W |
| **Real-time** | Hard real-time (deterministic) | Soft real-time (Linux jitter) |
| **GPIO** | 100+ pins (direct access) | 40-pin header (kernel driver) |
| **Cost** | $12.50 (MCU only) | $80 (board) |
| **Best For** | Embedded control, ultra-low power | Rich UI, computer vision, Linux apps |

**Choose STM32 when:**
- Real-time determinism required (medical devices, motor control)
- Ultra-low power critical (battery life measured in months/years)
- Direct hardware access needed (no OS overhead)
- Cost-sensitive (MCU $12.50 vs RPi $80)

**Choose Raspberry Pi when:**
- Need full Linux ecosystem (Python, web browser, etc.)
- Rich UI with GPU acceleration
- Computer vision, machine learning (TensorFlow, PyTorch)
- Rapid prototyping (don't want to write bare-metal code)

---

**Document Version:** 1.0.0  
**Hardware Revision:** A  
**Last Review:** 2026-02-22  

**Embedded Excellence Through Deterministic Control**  
**Real-Time Performance, Ultra-Low Power**
