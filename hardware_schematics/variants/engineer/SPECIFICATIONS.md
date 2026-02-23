# Engineer Variant - Technical Specifications

**Variant:** Engineer  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready

---

## Overview

The Engineer variant is designed for field engineering, diagnostics, troubleshooting, and remote system access. It integrates professional-grade measurement and analysis tools into a wrist-mounted form factor, enabling hands-free operation while maintaining full access to Project-AI's conversational intelligence.

---

## Domain-Specific Features

### 1. Integrated Multimeter
- **Voltage Measurement:** DC: ±60V (±0.1%), AC: 0-600V RMS (±0.5%)
- **Current Measurement:** DC/AC: 0-10A (±0.2%), with 200mA and 10A ranges
- **Resistance:** 0Ω to 60MΩ (±0.15%)
- **Continuity:** Audible beeper < 50Ω
- **Diode Test:** 0-2V forward voltage measurement
- **Capacitance:** 1nF to 10mF (±2%)
- **Frequency Counter:** 10Hz to 10MHz
- **ADC:** 24-bit Σ-Δ (ADS1263, Texas Instruments)
- **Input Protection:** 1000V CAT III rated, PTC + TVS diodes
- **Probe Interface:** 4mm banana jack connectors (retractable)

### 2. 2-Channel Digital Oscilloscope
- **Bandwidth:** DC to 20MHz (-3dB)
- **Sample Rate:** 100 MSa/s (interleaved), 50 MSa/s per channel
- **Memory Depth:** 32K samples per channel
- **Vertical Resolution:** 12-bit ADC (AD9042, Analog Devices)
- **Input Impedance:** 1MΩ || 20pF
- **Voltage Range:** ±50V (10x probe), ±5V (1x probe)
- **Timebase:** 10ns/div to 50s/div
- **Trigger Modes:** Edge, pulse width, video, slope
- **Analog Frontend:** LMH6518 (Texas Instruments) programmable gain amplifier
- **Probe Compensation:** Built-in 1kHz square wave calibration signal

### 3. Logic Analyzer
- **Channels:** 16 digital inputs
- **Sample Rate:** 200 MSa/s (max), 100 MSa/s (all channels)
- **Memory Depth:** 256K samples
- **Input Voltage:** 0-5V tolerant, 3.3V logic threshold
- **Protocol Decoders:** I2C, SPI, UART, 1-Wire, CAN, LIN, I2S
- **Capture IC:** CY7C68013A (Cypress USB controller) + FPGA (iCE40LP8K)
- **Trigger:** Pattern, edge, pulse, protocol-specific
- **Probe Connector:** 2x10 pin 0.1" header + flying leads

### 4. Function Generator
- **Waveforms:** Sine, square, triangle, sawtooth, pulse, noise, arbitrary
- **Frequency Range:** 0.1Hz to 10MHz
- **Amplitude:** 0-10Vpp (50Ω load), 0-20Vpp (high-Z load)
- **DC Offset:** ±10V
- **DAC:** AD9833 (Analog Devices) DDS function generator
- **Distortion:** < 1% THD (sine wave, 1kHz)
- **Output Impedance:** 50Ω
- **Modulation:** AM, FM, FSK, PWM
- **Arbitrary Waveform:** 4096-point buffer

### 5. Power Analysis
- **Power Measurement:** 0-60V, 0-10A, 600W max
- **Power Factor:** Calculation for AC circuits
- **Energy Logging:** kWh tracking with timestamp
- **Shunt Resistor:** 0.01Ω, 1%, 25W (Vishay WSL2512)
- **Sampling:** Simultaneous voltage and current (200kSa/s)

### 6. Thermal Imaging (Optional Module)
- **Sensor:** FLIR Lepton 3.5 (160x120 pixels, 57° HFOV)
- **Temperature Range:** -10°C to 400°C
- **Thermal Sensitivity:** <50mK NETD
- **Frame Rate:** 8.7 Hz
- **Interface:** SPI + I2C
- **Display Overlay:** PiP mode on main screen

### 7. CAD/Schematic Viewer
- **Formats:** PDF, DXF, DWG (via LibreCAD), Gerber (via KiCad)
- **Rendering:** OpenGL ES 3.0 hardware acceleration
- **Zoom:** 0.1x to 100x with layer control
- **Measurement Tools:** Distance, angle, area calculation
- **Annotation:** Touch-based markup and notes

### 8. Remote Access Suite
- **SSH Client:** OpenSSH 9.x with key-based authentication
- **RDP Client:** FreeRDP 2.x for Windows remote desktop
- **VNC Client:** TigerVNC with encryption
- **Serial Console:** UART, USB-Serial, Bluetooth Serial
- **Network Tools:** ping, traceroute, nmap, tcpdump
- **File Transfer:** SFTP, SCP, rsync

### 9. Cable & Connector Tester
- **Cable Types:** Ethernet (Cat5e/6/6a), USB (2.0/3.0), HDMI, VGA, Serial
- **Tests:** Continuity, wiremap, length (TDR), crosstalk
- **RJ45 Interface:** Built-in port with LED indicators
- **TDR Range:** 1m to 300m
- **TDR Resolution:** 0.3m (1 foot)

---

## Hardware Specifications

### Additional Sensors (Engineer-Specific)
- **LUX Meter:** BH1750FVI (0.11 to 100,000 lux)
- **Sound Level Meter:** MEMS microphone with dB(A) weighting (30-130 dB)
- **Vibration Sensor:** 3-axis accelerometer (±16g, ADXL345)
- **Magnetic Field:** 3-axis magnetometer (±8 gauss, MAG3110)

### Expansion Modules
- **Slot 1:** High-speed analog frontend (oscilloscope/multimeter)
- **Slot 2:** Logic analyzer FPGA module
- **Slot 3:** Thermal camera (optional)
- **Slot 4:** RF spectrum analyzer (optional, 1MHz-6GHz)

### Connector Panel (Side-Mounted)
```
┌─────────────────────────────────┐
│  [BNC CH1]  [BNC CH2]  [FUNC]   │  Oscilloscope & Function Gen
│  [4mm +]    [4mm -]    [COM]    │  Multimeter Probes  
│  [2x10 HDR]                     │  Logic Analyzer
│  [RJ45]     [USB-A]             │  Ethernet Tester & USB
└─────────────────────────────────┘
```

### Power Budget (Engineer Variant)
- **Idle:** 2.5W (display on, sensors active)
- **Multimeter:** +0.3W
- **Oscilloscope (active):** +1.2W
- **Logic Analyzer (capturing):** +0.8W
- **Thermal Camera:** +0.6W
- **Function Generator:** +0.4W
- **Maximum Load:** 5.8W
- **Battery Life:** 5.5 hours (continuous use), 12 hours (intermittent)

---

## Schematic Overview

### Analog Input Stage (Multimeter/Oscilloscope)

```
Input Protection                 Conditioning               ADC
┌──────────────┐             ┌──────────────┐        ┌──────────┐
│   TVS Diode  │   PTC       │  Attenuator  │  PGA   │ ADS1263  │
│   SMBJ60CA   ├───[100]─────┤  Resistive   ├────────┤  24-bit  ├──> MCU
│   ±60V       │             │  Divider     │LMH6518 │  Σ-Δ ADC │   (SPI)
└───────┬──────┘             └──────────────┘        └──────────┘
        │                           │
        └─────────[10MΩ]───────────┴─── Input Impedance
```

**Key Components:**
- **TVS Diode:** SMBJ60CA (Littelfuse) - 60V bidirectional protection
- **PTC Fuse:** 0ZCJ0100FF2E (Bel Fuse) - 1A hold, 100A trip
- **Input Divider:** Vishay foil resistors (0.01% tolerance)
- **PGA:** LMH6518 (Texas Instruments) - programmable gain 0dB to +40dB
- **ADC:** ADS1263 (Texas Instruments) - 38.4kSa/s, 24-bit

### Logic Analyzer Frontend

```
Input Buffers              Level Shifter        FPGA Capture
┌──────────────┐        ┌──────────────┐    ┌──────────────┐
│  74LVC244    │        │  TXS0108E    │    │  iCE40LP8K   │
│  8-bit Buffer├────────┤  8-ch Lvl    ├────┤  Pattern     ├──> USB
│  (x2 for 16) │  3.3V  │  Shifter     │    │  Recognition │   FIFO
└──────────────┘        └──────────────┘    └──────────────┘
     ↑
     │ 100Ω series resistor per input
     │ ESD protection diodes to 3.3V/GND
```

**Key Components:**
- **Input Buffers:** 74LVC244 (NXP) x2 - 5V tolerant inputs
- **Level Shifter:** TXS0108E (Texas Instruments) - bidirectional, auto-direction
- **FPGA:** iCE40LP8K (Lattice) - 7680 LUTs, 128Kb RAM, open-source toolchain
- **USB Interface:** CY7C68013A (Cypress) - USB 2.0 high-speed (480 Mbps)

### Oscilloscope Analog Frontend

```
Input           Attenuator        PGA              ADC
[BNC] ──[1MΩ]──┬─[10:1]──┬────┬─[Gain]─────────┬─[AD9042]──> FPGA
                │         │    │  LMH6518       │  12-bit     (Data)
                │  [1:1]──┘    │  0-40dB        │  40 MSa/s
                │               │                │
                └──[Coupling]───┘                │
                   AC/DC/GND                     └─[Trigger]──> MCU
```

**Key Components:**
- **Input Coupling:** Relays (Omron G6K-2F) for AC/DC/GND selection
- **Attenuator:** Precision resistor network (0.1% tolerance)
- **PGA:** LMH6518 (Texas Instruments) - 20MHz bandwidth
- **ADC:** AD9042 (Analog Devices) - 12-bit, 40 MSa/s per channel
- **Trigger Comparator:** LT1016 (Analog Devices) - ultra-fast comparator

### Function Generator

```
MCU (SPI) ──> AD9833 ──> LPF ──> VGA ──> Output Amp ──> [BNC]
              DDS       Bessel   AD8336   OPA2134      50Ω Out
              10-bit    5-pole   0-20dB   Rail-Rail
```

**Key Components:**
- **DDS:** AD9833 (Analog Devices) - 25MHz clock, 10-bit DAC
- **Low-Pass Filter:** 5-pole Bessel, 10MHz cutoff (op-amp based)
- **VGA:** AD8336 (Analog Devices) - voltage-controlled attenuator
- **Output Amp:** OPA2134 (Texas Instruments) - low-noise, high-speed op-amp
- **Output Protection:** 10Ω series resistor + clamping diodes

---

## Bill of Materials (Engineer-Specific Components)

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| 24-bit ADC | ADS1263IPWR | Mouser | 2 | $12.45 | $24.90 |
| 12-bit ADC | AD9042AKSZ | DigiKey | 2 | $18.75 | $37.50 |
| PGA | LMH6518SQ | Mouser | 2 | $8.90 | $17.80 |
| DDS Function Gen | AD9833BRMZ | DigiKey | 1 | $4.65 | $4.65 |
| FPGA | iCE40LP8K-SG121 | Mouser | 1 | $15.20 | $15.20 |
| USB Controller | CY7C68013A-56LTXC | DigiKey | 1 | $7.40 | $7.40 |
| Input Buffers | 74LVC244APW | Mouser | 2 | $0.85 | $1.70 |
| Level Shifter | TXS0108EPWR | DigiKey | 2 | $1.20 | $2.40 |
| TVS Diodes | SMBJ60CA | Mouser | 4 | $0.45 | $1.80 |
| Precision Resistors | Z201 Series (Vishay) | DigiKey | 20 | $1.25 | $25.00 |
| BNC Connectors | 5227161-1 (TE) | Mouser | 3 | $2.15 | $6.45 |
| 4mm Banana Jacks | 108-0902-001 (Emerson) | DigiKey | 3 | $1.85 | $5.55 |
| RJ45 Jack | SS-7188S-NF | Mouser | 1 | $0.95 | $0.95 |
| 2x10 Pin Header | TSW-110-07-G-D | DigiKey | 1 | $1.45 | $1.45 |
| **Subtotal (Engineer Components)** | | | | | **$152.75** |

*Note: Prices are estimates from 2026 Q1. Add base Pip-Boy cost ($85-$110) for total unit cost.*

---

## Software Integration

### Firmware Components
- **Oscilloscope DSP:** FFT analysis, trigger detection, waveform capture
- **Logic Analyzer:** Protocol decoders (I2C, SPI, UART, CAN)
- **Multimeter:** Autoranging, true RMS calculation, data logging
- **Function Generator:** Waveform synthesis, modulation engines
- **CAD Viewer:** PDF rendering (Poppler), DXF parser, Gerber viewer

### Project-AI Integration
- **Voice Commands:** "Measure voltage on probe 1", "Capture waveform on channel 2"
- **Intelligent Analysis:** Automatic circuit identification, component value reading via OCR
- **Troubleshooting Assistant:** Step-by-step diagnostic guidance
- **Remote Collaboration:** Screen sharing via WebRTC for remote support
- **Documentation:** Auto-generate measurement reports with screenshots

### Machine Learning Features
- **Waveform Classification:** Identify signal types (PWM, UART, SPI, etc.)
- **Anomaly Detection:** Flag unusual patterns in captured data
- **Component Recognition:** OCR for resistor color codes, IC markings
- **Fault Prediction:** Analyze trends in power measurements

---

## Calibration & Testing

### Factory Calibration
1. **Multimeter:** NIST-traceable reference (Fluke 8846A)
2. **Oscilloscope:** Calibrated signal generator (Keysight 33500B)
3. **Logic Analyzer:** Known-good protocol sources
4. **Function Generator:** Spectrum analyzer verification (Rigol DSA815)

### User Calibration
- **Probe Compensation:** On-screen wizard with 1kHz square wave
- **DC Offset:** Auto-zero routine for ADC offset correction
- **Gain Calibration:** Reference voltage measurement and correction

### Validation Tests
- **Multimeter Accuracy:** 10V DC reference (±0.01%)
- **Oscilloscope Bandwidth:** -3dB point verification at 20MHz
- **Logic Analyzer Timing:** Sample clock accuracy measurement
- **Function Generator Distortion:** THD measurement < 1%

---

## Safety & Compliance

### Electrical Safety
- **Input Protection:** CAT III 1000V rated
- **Fusing:** PTC resettable fuses on all inputs
- **Isolation:** Optocouplers for USB/computer connection
- **Warning Labels:** High voltage warnings on probe connectors

### Regulatory Compliance
- **CE Marking:** EN 61010-1 (safety), EN 61326-1 (EMC)
- **FCC Part 15:** Class B digital device
- **RoHS:** Compliant (lead-free soldering)
- **WEEE:** End-of-life recycling program

---

## Usage Examples

### Example 1: Debugging a Microcontroller
```
1. Connect logic analyzer to I2C bus (SDA, SCL)
2. Voice command: "Capture I2C traffic"
3. Project-AI decodes addresses and data
4. Auto-detects protocol errors (missing ACKs, bus contention)
5. Generates diagnostic report with recommendations
```

### Example 2: Power Supply Analysis
```
1. Connect multimeter probes to PSU output
2. Voice command: "Monitor voltage and current"
3. Real-time waveform display shows ripple
4. Oscilloscope measures ripple frequency and amplitude
5. Power calculation shows efficiency and power factor
```

### Example 3: Signal Integrity Testing
```
1. Connect function generator to circuit under test
2. Voice command: "Generate 1MHz square wave"
3. Oscilloscope captures response on both channels
4. FFT analysis shows harmonic content
5. Eye diagram mode for digital signal quality
```

---

## Maintenance & Support

### Recommended Accessories
- **Probe Set:** 10:1 oscilloscope probes (Tektronix P6139B or equivalent)
- **Multimeter Leads:** Silicone test leads with banana plugs
- **Logic Analyzer Probes:** 16-channel flying lead set
- **Calibration Kit:** Voltage/resistance reference standards
- **Carry Case:** Padded hard case with foam insert

### Consumables
- **Probe Tips:** Replace every 6-12 months with heavy use
- **Battery:** Replace after 500 charge cycles (~2 years)
- **Screen Protector:** Replace if scratched or damaged

### Repair Parts Availability
- **All major ICs:** Available from Mouser, DigiKey, Arrow
- **Connectors:** Standard catalog parts (TE, Amphenol)
- **PCB:** Gerber files available for reproduction
- **Firmware:** Open-source, community-maintained

---

## Appendix A: Measurement Accuracy Specifications

### DC Voltage (ADS1263, 24-bit ADC)
| Range | Resolution | Accuracy (23°C ±5°C) | Accuracy (Full Temp) |
|-------|-----------|---------------------|---------------------|
| ±60mV | 1μV | ±0.02% + 5μV | ±0.05% + 10μV |
| ±600mV | 10μV | ±0.03% + 50μV | ±0.08% + 100μV |
| ±6V | 100μV | ±0.05% + 500μV | ±0.12% + 1mV |
| ±60V | 1mV | ±0.1% + 5mV | ±0.2% + 10mV |

### DC Current
| Range | Resolution | Accuracy | Burden Voltage |
|-------|-----------|----------|---------------|
| ±200mA | 1μA | ±0.15% + 50μA | < 200mV |
| ±10A | 100μA | ±0.3% + 5mA | < 500mV |

### Resistance
| Range | Resolution | Accuracy | Test Current |
|-------|-----------|----------|-------------|
| 600Ω | 0.01Ω | ±0.2% + 0.1Ω | 1mA |
| 6kΩ | 0.1Ω | ±0.15% + 0.5Ω | 100μA |
| 60kΩ | 1Ω | ±0.15% + 5Ω | 10μA |
| 600kΩ | 10Ω | ±0.2% + 50Ω | 1μA |
| 6MΩ | 100Ω | ±0.5% + 500Ω | 100nA |
| 60MΩ | 1kΩ | ±1.5% + 5kΩ | 10nA |

---

## Appendix B: Pinout Diagrams

### Logic Analyzer Connector (2x10, 0.1" pitch)
```
  GND  1  2  CH0
  GND  3  4  CH1
  GND  5  6  CH2
  GND  7  8  CH3
  GND  9 10  CH4
  GND 11 12  CH5
  GND 13 14  CH6
  GND 15 16  CH7
  GND 17 18  CH8-CH15 (optional)
 +3.3V19 20  CLK (external clock input)
```

### Oscilloscope BNC Connectors
- **CH1 BNC:** Signal input (center conductor = signal, shield = ground)
- **CH2 BNC:** Signal input (center conductor = signal, shield = ground)
- **FUNC BNC:** Function generator output (50Ω source impedance)

### Multimeter Banana Jacks
- **RED (+):** Positive input (voltage, resistance, diode, continuity)
- **BLACK (COM):** Common ground reference
- **YELLOW (10A):** High-current input (current measurement > 200mA)

---

**Document Version:** 1.0.0  
**Hardware Revision:** A  
**Last Review:** 2026-02-22
