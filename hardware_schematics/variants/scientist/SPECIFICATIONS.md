# Scientist Variant - Technical Specifications

**Variant:** Scientist  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready

---

## Overview

The Scientist variant is optimized for laboratory research, data collection, and experiment monitoring. It integrates laboratory-grade sensors and instrumentation, enabling real-time data acquisition, analysis, and remote equipment control while maintaining full access to Project-AI's analytical intelligence.

---

## Domain-Specific Features

### 1. Integrated Spectrometer
- **Type:** Miniature UV-Vis-NIR spectrometer
- **Wavelength Range:** 340nm to 1000nm
- **Optical Resolution:** <10nm FWHM @ 546nm
- **Sensor:** Hamamatsu C12880MA micro-spectrometer
- **Integration Time:** 1.5ms to 10s (programmable)
- **Dynamic Range:** 10,000:1
- **Interface:** I2C + clock + trigger
- **Light Source:** Integrated LED (white, UV options)
- **Applications:** Absorbance, transmittance, reflectance, fluorescence

### 2. pH Meter & Ion-Selective Electrodes
- **pH Range:** 0.00 to 14.00 pH
- **pH Resolution:** 0.01 pH
- **pH Accuracy:** ±0.02 pH @ 25°C
- **Temperature Compensation:** Automatic (0-100°C range)
- **mV Measurement:** ±2000mV (for ISE electrodes)
- **Reference:** Ag/AgCl gel-filled electrode (replaceable)
- **Probe Connector:** BNC with built-in temperature sensor (PT1000)
- **ADC:** ADS1220 (Texas Instruments) - 24-bit, low-noise
- **Calibration:** Multi-point (up to 5 buffers) with auto-recognition

### 3. Advanced Environmental Sensors
- **Temperature:** -40°C to 125°C (±0.1°C, PT1000 RTD)
- **Humidity:** 0-100% RH (±1.5%, Sensirion SHT40)
- **Barometric Pressure:** 300-1100 hPa (±0.5 hPa, Bosch BMP390)
- **Air Quality (VOC):** Sensirion SGP40 (MOx sensor, 0-500 VOC index)
- **CO₂:** SCD41 (Sensirion) - NDIR, 400-5000ppm (±40ppm + 5%)
- **Particulate Matter:** PMS5003 (Plantower) - PM1.0, PM2.5, PM10
- **UV Index:** VEML6075 (Vishay) - UVA + UVB
- **Lux/Illuminance:** TSL2591 (AMS) - 188 μLux to 88,000 Lux

### 4. Precision Thermometry
- **Thermocouple Inputs:** 4 channels (Type K, J, T, E, N, R, S)
- **RTD Inputs:** 2 channels (PT100, PT1000, 2/3/4-wire)
- **AFE:** MAX31856 (Maxim) - cold-junction compensated
- **Resolution:** 0.0078125°C (19-bit)
- **Accuracy:** ±0.15°C (Type K, -200°C to 1372°C)
- **Update Rate:** 1-16 Hz (configurable)
- **Connector:** Mini thermocouple jacks (Omega compatible)

### 5. Electrochemistry Module
- **Potentiostat:** 3-electrode configuration (WE, RE, CE)
- **Voltage Range:** ±5V (working electrode)
- **Current Range:** 10nA to 100mA (auto-ranging)
- **Techniques:** Cyclic voltammetry, chronoamperometry, impedance spectroscopy
- **Scan Rate:** 0.001 to 1000 mV/s
- **AFE:** LMP91000 (Texas Instruments) - configurable AFE
- **Applications:** Sensor characterization, corrosion studies, battery testing

### 6. Conductivity/TDS Meter
- **Conductivity Range:** 0.1 μS/cm to 200 mS/cm
- **TDS Range:** 0 to 100,000 ppm (mg/L)
- **Salinity:** 0 to 80 ppt
- **Cell Constant:** Automatic detection (K=0.1, 1.0, 10)
- **Probe:** 4-electrode conductivity cell (temperature compensated)
- **Temperature Compensation:** Linear/non-linear (NaCl, KCl curves)

### 7. Lab Equipment Control Interface
- **RS-232/RS-485:** Full-duplex serial (programmable baud rate)
- **GPIB (IEEE-488):** Optional USB-GPIB adapter support
- **Ethernet/WiFi:** Remote instrument control (SCPI, ModBus)
- **Analog Control:** 0-10V / 4-20mA outputs (2 channels)
- **Relay Outputs:** 4x SPDT (5A @ 250VAC) - stirrer, heater, pump control
- **Supported Devices:** Pumps, stirrers, thermostats, shakers, centrifuges

### 8. Sample Imaging & Documentation
- **Microscope Adapter:** USB microscope (1920x1080, 1000x magnification)
- **Barcode Scanner:** 1D/2D barcode reader (Code 128, QR, Data Matrix)
- **Document Camera:** 13MP autofocus (sample vials, labels, notebooks)
- **Macro Mode:** Focus range 2cm to infinity
- **Illumination:** LED ring light with adjustable intensity

### 9. Data Logging & Analysis
- **Sampling Rates:** 0.1 Hz to 1 kHz (sensor-dependent)
- **Storage:** Unlimited (microSD card), cloud sync
- **Formats:** CSV, HDF5, JSON, LabView TDM/TDMS
- **Real-Time Plotting:** Multi-channel strip charts, XY plots
- **Statistics:** Mean, SD, RSD, min/max, regression
- **Alerts:** Threshold-based alarms (email, SMS, local notification)

---

## Hardware Specifications

### Additional Sensors (Scientist-Specific)
- **Dissolved Oxygen:** Optical DO sensor (0-20 mg/L, ±0.1 mg/L)
- **ORP (Redox):** ±2000mV measurement (platinum electrode)
- **Turbidity:** Nephelometric sensor (0-1000 NTU)
- **Chlorine:** Free/total chlorine sensor (0-10 ppm)

### Expansion Modules
- **Slot 1:** Spectrometer optical bench
- **Slot 2:** Electrochemistry potentiostat
- **Slot 3:** Multi-input thermocouple module
- **Slot 4:** Liquid chromatography detector (optional)

### Connector Panel (Side-Mounted)
```
┌──────────────────────────────────────┐
│  [BNC pH]   [BNC ORP]  [TC1-4]       │  Electrochemical Sensors
│  [4-pole Cond] [DO Optical]          │  Conductivity & DO
│  [Fiber Input] [LED Out]             │  Spectrometer
│  [Relay 1-4]  [Analog Out]           │  Lab Equipment Control
└──────────────────────────────────────┘
```

### Power Budget (Scientist Variant)
- **Idle:** 2.8W (display on, sensors active)
- **Spectrometer (active):** +0.5W
- **pH/ORP Measurement:** +0.2W
- **Environmental Sensors:** +0.4W
- **CO₂ Sensor:** +0.15W
- **Relay Outputs (all active):** +0.6W
- **Maximum Load:** 4.65W
- **Battery Life:** 6.5 hours (continuous use), 14 hours (intermittent)

---

## Schematic Overview

### pH Meter Frontend

```
pH Probe (BNC)          Amplifier            ADC
┌──────────────┐      ┌──────────────┐    ┌──────────┐
│  Glass        │      │  OPA2333     │    │ ADS1220  │
│  Electrode    ├──────┤  High-Z      ├────┤  24-bit  ├──> MCU
│  (High-Z)     │      │  Buffer      │    │  PGA     │   (SPI)
└───────┬───────┘      └──────────────┘    └──────────┘
        │                    ↑
        │              Temperature
        │              PT1000 RTD
        └──────────────────────────────> Auto Compensation
```

**Key Components:**
- **Input Buffer:** OPA2333 (Texas Instruments) - CMOS, ultra-low bias current (<1pA)
- **ADC:** ADS1220 (Texas Instruments) - 24-bit, 2kSa/s, internal PGA
- **Temperature Sensor:** PT1000 RTD (±0.1°C, IEC 60751 Class A)
- **BNC Connector:** Amphenol 31-221-RFX (isolated, low-noise)
- **ESD Protection:** TPD1E05U06 (Texas Instruments) - ±8kV contact

### Spectrometer Interface

```
Light Input → [Diffraction Grating] → [Linear CCD Array] → ADC → MCU
   Fiber         600 lines/mm         128 pixels          12-bit  I2C
   (SMA905)      340-1000nm           25μm pitch          C12880MA

Trigger ←──[MCU GPIO]
Clock   ←──[MCU GPIO]
LED Driver ←──[PWM]──[TPS61169]──> White LED (5W)
```

**Key Components:**
- **Spectrometer:** C12880MA (Hamamatsu) - 128-element linear array
- **Fiber Input:** SMA905 connector with FC/PC adapter
- **LED Driver:** TPS61169 (Texas Instruments) - boost converter, PWM dimming
- **Light Source:** OSRAM LCW W5SM (white, 5W, 350 lm @ 1A)

### Thermocouple Amplifier

```
TC Input (K-type)      AFE                  ADC             MCU
┌──────────────┐   ┌──────────────┐    ┌──────────┐       SPI
│  Thermocouple │   │  MAX31856    │    │ Internal │   ┌────────┐
│  +/-          ├───┤  Cold Jun.   ├────┤  19-bit  ├───┤  MCU   │
│  Type K,J,etc │   │  Compensation│    │  Σ-Δ ADC │   │        │
└───────────────┘   └──────────────┘    └──────────┘   └────────┘
                            ↑
                      Internal Temp
                      Sensor (±0.5°C)
```

**Key Components:**
- **AFE:** MAX31856 (Maxim) - precision thermocouple-to-digital converter
- **Connector:** Mini thermocouple jack (Omega HMPW-K-M)
- **Protection:** TVS diodes + series resistors (1kΩ)

---

## Bill of Materials (Scientist-Specific Components)

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| Micro-Spectrometer | C12880MA | Hamamatsu | 1 | $85.00 | $85.00 |
| pH ADC | ADS1220IPWR | Mouser | 1 | $5.80 | $5.80 |
| High-Z Op-Amp | OPA2333AIDR | DigiKey | 2 | $3.25 | $6.50 |
| TC-to-Digital | MAX31856MUA+ | Mouser | 4 | $7.20 | $28.80 |
| CO₂ Sensor | SCD41-D-R2 | DigiKey | 1 | $42.00 | $42.00 |
| VOC Sensor | SGP40-D-R4 | Mouser | 1 | $8.50 | $8.50 |
| PM Sensor | PMS5003 | Plantower | 1 | $15.00 | $15.00 |
| Humidity Sensor | SHT40-AD1B | DigiKey | 1 | $2.10 | $2.10 |
| Pressure Sensor | BMP390L | Mouser | 1 | $4.50 | $4.50 |
| UV Sensor | VEML6075 | DigiKey | 1 | $1.85 | $1.85 |
| Light Sensor | TSL2591FN | Mouser | 1 | $5.20 | $5.20 |
| Potentiostat AFE | LMP91000SDE | DigiKey | 1 | $8.95 | $8.95 |
| LED Driver | TPS61169DCKR | Mouser | 1 | $1.65 | $1.65 |
| Relay (SPDT) | G6K-2F-Y-DC5 | DigiKey | 4 | $2.40 | $9.60 |
| BNC Connectors | 31-221-RFX | Mouser | 4 | $3.50 | $14.00 |
| SMA905 Fiber | 905-F-S-M-20 | Thorlabs | 1 | $12.50 | $12.50 |
| PT1000 RTD | M222PT1000 | Omega | 2 | $25.00 | $50.00 |
| **Subtotal (Scientist Components)** | | | | | **$301.95** |

*Note: Prices are estimates from 2026 Q1. Add base Pip-Boy cost ($85-$110) for total unit cost.*

---

## Software Integration

### Firmware Components
- **Spectroscopy Engine:** Wavelength calibration, baseline correction, peak detection
- **pH Calibration:** Multi-point (1-5 buffers) with Nernst equation
- **Thermocouple Processing:** Polynomial conversion (NIST ITS-90)
- **Data Logger:** High-speed acquisition with timestamp synchronization
- **Equipment Drivers:** SCPI parser, ModBus RTU/TCP, custom protocols

### Project-AI Integration
- **Voice Commands:** "Measure pH", "Start spectrometer scan", "Log temperature for 1 hour"
- **Intelligent Analysis:** Spectral peak identification, concentration calculation
- **Experiment Assistant:** Protocol suggestions, safety warnings, data interpretation
- **Literature Search:** Chemical properties lookup, citation manager
- **Report Generation:** LaTeX/Markdown reports with embedded plots

### Machine Learning Features
- **Spectral Classification:** Compound identification via spectral library matching
- **Anomaly Detection:** Out-of-range measurements, drift detection
- **Predictive Maintenance:** Electrode aging prediction, calibration reminders
- **Experiment Optimization:** Parameter sweeps, design of experiments (DoE)

---

## Calibration & Testing

### Factory Calibration
1. **pH Meter:** NIST-traceable buffers (pH 4.01, 7.00, 10.01)
2. **Spectrometer:** Wavelength calibration (Hg-Ar lamp, known emission lines)
3. **Thermocouples:** Ice point (0°C) and boiling point (100°C) verification
4. **Conductivity:** Standard solutions (84 μS/cm, 1413 μS/cm, 12.88 mS/cm)

### User Calibration
- **pH:** 1, 2, or 3-point calibration with auto-buffer recognition
- **Spectrometer:** Dark spectrum capture, reference lamp calibration
- **Thermocouple:** Offset correction at known temperature
- **Conductivity:** Cell constant adjustment with standard solution

### Validation Tests
- **pH Accuracy:** ±0.02 pH across range (NIST buffers)
- **Spectral Resolution:** <10nm FWHM using laser source
- **Temperature Accuracy:** ±0.15°C (Type K, -200 to 1300°C)
- **Conductivity Linearity:** R² > 0.999 (log-log plot)

---

## Safety & Compliance

### Chemical Safety
- **IP67 Rating:** Splash-proof, chemical-resistant case
- **Chemical Compatibility:** PTFE/PVDF wetted parts (acid/base resistant)
- **Emergency Wash:** Quick-release probe connectors for emergency removal
- **Material Safety:** Compliant with OSHA, EPA lab safety standards

### Biological Safety
- **Disinfection:** UV-C sterilization mode (254nm LED, optional)
- **Contamination Prevention:** Disposable probe sleeves, sterile technique support
- **Bio-Waste Handling:** Guidance for proper disposal (Project-AI knowledge base)

### Regulatory Compliance
- **CE Marking:** EN 61010-1 (laboratory equipment safety)
- **ISO 17025:** Measurement traceability to NIST standards
- **EPA Method Compliance:** Water quality testing methods (200 series)
- **GLP/GMP:** Good Laboratory Practice documentation support

---

## Usage Examples

### Example 1: Water Quality Testing
```
1. Calibrate pH meter with 3-point buffers (4.01, 7.00, 10.01)
2. Connect pH probe to sample
3. Voice command: "Measure water quality parameters"
4. Device measures pH, conductivity, TDS, temperature, DO
5. Project-AI compares to EPA/WHO drinking water standards
6. Report generated with pass/fail for each parameter
```

### Example 2: UV-Vis Spectroscopy
```
1. Prepare sample in 1cm cuvette
2. Voice command: "Acquire UV-Vis spectrum"
3. Spectrometer scans 340-1000nm
4. Project-AI identifies absorption peaks
5. Beer-Lambert law applied for concentration calculation
6. Results exported to LIMS (Laboratory Information Management System)
```

### Example 3: Temperature Profiling
```
1. Connect 4 Type K thermocouples to reactor vessel
2. Voice command: "Monitor reaction temperature for 2 hours"
3. Data logged at 1 Hz with timestamp
4. Real-time plot shows all 4 channels
5. Alarms triggered if temperature exceeds setpoint ±5°C
6. CSV file exported with statistics (min, max, mean, SD)
```

---

## Maintenance & Support

### Recommended Accessories
- **pH Electrode:** Glass combination electrode (gel-filled, refillable)
- **Conductivity Cell:** 4-electrode probe (K=1.0, epoxy body)
- **Thermocouples:** Type K probes (various lengths, stainless sheath)
- **Cuvettes:** 1cm path length, quartz or polystyrene (UV-Vis)
- **Calibration Standards:** pH buffers, conductivity standards, certified reference materials

### Consumables
- **pH Electrode:** Replace every 12-18 months
- **Reference Electrode Fill Solution:** 3M KCl (refill monthly)
- **Conductivity Cell:** Clean with dilute HCl every 6 months
- **Spectrometer:** Optical fiber (replace if damaged)

### Repair Parts Availability
- **Electrodes:** Standard form factors (compatible with Thermo/Mettler/Hach)
- **Sensors:** All components available from major distributors
- **PCB:** Gerber files and assembly documentation available
- **Firmware:** Open-source, community-maintained

---

## Appendix A: Measurement Specifications

### pH Measurement (ADS1220 + OPA2333)
| Parameter | Specification |
|-----------|---------------|
| Range | 0.00 to 14.00 pH |
| Resolution | 0.01 pH |
| Accuracy | ±0.02 pH @ 25°C |
| Repeatability | ±0.01 pH |
| Response Time | <3 seconds (90% final value) |
| Temperature Compensation | 0-100°C, automatic |
| Input Impedance | >10¹² Ω |
| Offset Drift | <0.02 pH/year |

### Spectrometer (Hamamatsu C12880MA)
| Parameter | Specification |
|-----------|---------------|
| Wavelength Range | 340-1000 nm |
| Wavelength Accuracy | ±1 nm |
| Optical Resolution | <10 nm FWHM @ 546 nm |
| Stray Light | <0.3% @ 340 nm |
| Signal-to-Noise Ratio | 3000:1 (typical) |
| Integration Time | 1.5 ms to 10 s |
| Dynamic Range | 10,000:1 |
| Linearity | >99% (R² > 0.99) |

### Thermocouple (MAX31856)
| Type | Range | Accuracy |
|------|-------|----------|
| K | -200°C to 1372°C | ±0.15°C (typical) |
| J | -210°C to 1200°C | ±0.15°C |
| T | -200°C to 400°C | ±0.15°C |
| E | -200°C to 1000°C | ±0.15°C |
| N | -200°C to 1300°C | ±0.15°C |
| R | -50°C to 1768°C | ±0.5°C |
| S | -50°C to 1768°C | ±0.5°C |

---

## Appendix B: Chemical Compatibility

### Probe Materials
- **pH Glass:** Borosilicate (resistant to most acids/bases)
- **Reference Junction:** Ceramic frit (porous, self-cleaning)
- **Probe Body:** PEI plastic (chemically resistant, autoclavable)
- **O-Rings:** Viton (fluorocarbon, broad chemical resistance)

### Compatible Solutions
- **Acids:** HCl, H₂SO₄, HNO₃, H₃PO₄ (dilute to concentrated)
- **Bases:** NaOH, KOH, NH₄OH (up to 1M)
- **Solvents:** Water, ethanol, methanol, acetone (avoid prolonged exposure)
- **Buffers:** Phosphate, citrate, borate, tris

### Incompatible Solutions
- **Strong Oxidizers:** Concentrated peroxides, permanganate (damages glass)
- **HF (Hydrofluoric Acid):** Etches glass (use plastic-body electrodes)
- **Tris Buffer above pH 9:** Causes junction clogging (use KCl-free reference)

---

**Document Version:** 1.0.0  
**Hardware Revision:** A  
**Last Review:** 2026-02-22
