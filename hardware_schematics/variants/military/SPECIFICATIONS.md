# Military Variant - Technical Specifications

**Variant:** Military  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready  
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY (FOUO)  
**Compliance:** MIL-STD-810H, MIL-STD-461G, NIST SP 800-53, NSA Suite B Cryptography

---

## Overview

The Military variant is designed for tactical operations, mission planning, secure communications, and soldier systems integration. It provides enhanced situational awareness, blue force tracking, encrypted communications, threat detection, and interoperability with military C4ISR systems (Command, Control, Communications, Computers, Intelligence, Surveillance, and Reconnaissance).

**RESTRICTED TO AUTHORIZED MILITARY PERSONNEL ONLY**  
**EXPORT CONTROLLED:** ITAR Category XI, ECCN 5A992, EAR99

---

## Domain-Specific Features

### 1. Tactical GPS & SAASM
- **GPS Module:** u-blox ZED-F9P with SAASM (Selective Availability Anti-Spoofing Module)
- **Anti-Jam (AJ):** Nullsteering antenna array (4-element)
- **Anti-Spoof (AS):** M-Code reception (requires NSA key)
- **Accuracy:** <3m CEP (civilian), <1m CEP (military signals)
- **Update Rate:** 20 Hz (50ms)
- **MGRS Coordinate Display:** Military Grid Reference System
- **DAGR Compatibility:** Defense Advanced GPS Receiver protocol
- **Altitude:** ±5m accuracy, barometric fusion
- **Datum:** WGS84, custom military datums (loadable)

### 2. Secure Tactical Radio
- **Waveform:** SINCGARS (Single Channel Ground and Airborne Radio System)
- **Frequency:** 30-87.975 MHz (VHF-FM), 225-399.975 MHz (UHF-AM)
- **Channels:** 2320 (SINCGARS VHF), 7000 (UHF)
- **Encryption:** AES-256, Type 1 (NSA-certified)
- **ECCM:** Frequency Hopping (FH), 111 hops/second
- **Power Output:** 5W (max), 1W (low power)
- **Range:** 5km (handheld), 10km (vehicle-mounted antenna)
- **Interoperability:** ASIP, EPLRS, SATCOM (optional modules)
- **COMSEC:** Type 1 encryption fill device (KYK-13, KOI-18)

### 3. Blue Force Tracking (BFT)
- **Network:** Iridium SATCOM + L-band military SATCOM (optional)
- **Update Rate:** 30 seconds (peacetime), 5 seconds (combat)
- **Friendly Positions:** Display up to 500 units on tactical map
- **IFF Integration:** Mode 4/5 Interrogator (identify friend or foe)
- **FBCB2/JBC-P:** Force XXI Battle Command Brigade and Below integration
- **SA (Situational Awareness):** Real-time common operating picture (COP)
- **Coalition Forces:** Coalition chat, position sharing (with clearance)

### 4. Threat Detection Suite
- **CBRN Sensors:** Chemical, Biological, Radiological, Nuclear detection
  - **Chemical:** 6-sensor array (nerve, blister, blood agents)
  - **Radiation:** Geiger-Müller tube (0.001-1000 mSv/h)
  - **Biological:** Aerosol collector + reagent test (anthrax, ricin, botulinum)
- **Laser Warning Receiver:** 360° coverage, range finder detection
- **RF Detector:** Sweeps 20MHz-6GHz (IED triggers, jammers, cell phones)
- **Acoustic Shot Detection:** Gunfire triangulation (rifle, small arms, explosives)
- **Seismic Sensor:** Ground vibration (vehicle approach, footsteps)

### 5. Night Vision & Thermal Imaging
- **Image Intensifier:** Gen 3+ Night Vision (built-in OLED display overlay)
- **Thermal Camera:** FLIR Lepton 3.5 (160x120, 57° HFOV, <50mK NETD)
- **Temperature Range:** -20°C to 550°C
- **Display Modes:** White-hot, black-hot, rainbow, iron palette
- **Sensor Fusion:** NV + thermal composite image
- **Automatic Gain Control:** Real-time brightness adjustment

### 6. Mission Planning & Navigation
- **Offline Maps:** DTED (Digital Terrain Elevation Data), Level 1/2
- **Tactical Overlays:** Military graphics (NATO APP-6D symbology)
- **Route Planning:** Waypoints, rally points, phase lines, boundaries
- **Air Corridors:** No-fly zones, artillery impact areas, airspace coordination
- **Target Coordination:** 10-digit MGRS, elevation, target description
- **SALUTE Reports:** Voice-to-text (Size, Activity, Location, Unit, Time, Equipment)

### 7. Encrypted Communications
- **Voice Encryption:** NSA Suite B Cryptography (AES-256, ECDH P-384)
- **Data Encryption:** AES-256-GCM for all data at rest and in transit
- **Key Management:** Over-the-air rekeying (OTAR), electronic key fill
- **PKI:** DoD Public Key Infrastructure certificates
- **COMSEC Alarm:** Tamper detection triggers crypto zeroization
- **Secure Messaging:** XMPP with OTR (Off-the-Record) messaging

### 8. Soldier Systems Integration
- **Nett Warrior:** Connects to Android Tactical Assault Kit (ATAK)
- **IVAS Integration:** Integrated Visual Augmentation System (HoloLens-based)
- **PEO Soldier:** Program Executive Office Soldier systems compatibility
- **Rifleman Radio:** Intra-squad voice/data (150m range, encrypted)
- **Body Sensors:** Heart rate, core temperature, hydration monitoring
- **Medical Alerts:** Casualty notification, location broadcast

### 9. Intelligence Collection
- **HUMINT:** Voice recording, photo documentation, biometric capture
- **SIGINT:** Signal intelligence (RF spectrum analysis, cell tower tracking)
- **IMINT:** Imagery intelligence (photo/video with metadata)
- **ELINT:** Electronic intelligence (emitter fingerprinting)
- **Upload to C4ISR:** Secure upload to command intelligence systems

---

## Hardware Specifications

### Ruggedization (MIL-STD-810H)
- **Drop Test:** 26 drops from 1.2m onto concrete (6 faces, 8 edges, 12 corners)
- **Vibration:** 15-2000 Hz, 5g peak (vehicle, helicopter profiles)
- **Shock:** 40g half-sine, 11ms duration
- **Temperature:** -40°C to 71°C (operational), -51°C to 71°C (storage)
- **Humidity:** 95% RH @ 60°C (10 days)
- **Rain:** IPX6 (heavy rain, 100 L/min for 30 min)
- **Dust:** IP6X (dust-tight, 8 hours in talcum powder)
- **Salt Fog:** 5% NaCl solution, 48 hours
- **Altitude:** 4,572m (15,000 ft) operational

### EMC/EMI (MIL-STD-461G)
- **Conducted Emissions:** CE101, CE102
- **Radiated Emissions:** RE101, RE102
- **Conducted Susceptibility:** CS101, CS114, CS115, CS116
- **Radiated Susceptibility:** RS103 (10 kHz-40 GHz, 200 V/m)
- **EMP Hardening:** 50 kV/m pulse (limited protection)

### Additional Sensors (Military-Specific)
- **Ballistic Shock Sensor:** Detects nearby bullet impacts
- **Barometric Altimeter:** ±1m altitude accuracy (parachute jumps)
- **Underwater Sensor:** Depth gauge (0-50m, diving operations)
- **Laser Range Finder:** 5m to 2km range (optional module)
- **Compass:** 3-axis magnetometer (±0.5°, compensated)

### Expansion Modules
- **Slot 1:** SINCGARS tactical radio
- **Slot 2:** SAASM GPS module
- **Slot 3:** CBRN sensor suite
- **Slot 4:** Laser warning receiver / RF detector

### Connector Panel (Sealed, IP67)
```
┌────────────────────────────────────┐
│  [MIL-DTL-38999] Radio Connector   │  Tactical Radio
│  [MIL-STD-461] Antenna Ports (x3)  │  GPS, VHF, UHF
│  [MIL-C-26482] Power (NATO)        │  External Power
│  [USB-C] Data (sealed cover)       │  Firmware Update
└────────────────────────────────────┘
```

### Power Budget (Military Variant)
- **Idle:** 3.5W (display off, GPS active, BFT standby)
- **Radio (receive):** +1.2W
- **Radio (transmit, 5W):** +8.5W (peak)
- **Thermal Camera:** +0.6W
- **CBRN Sensors:** +1.8W
- **Maximum Load:** 15.6W (all systems active, radio TX)
- **Battery Life:** 3 hours (high intensity ops), 8 hours (standard patrol)

### Extended Battery Options
- **Standard:** 3000mAh Li-Ion (11.1Wh) - 8 hours
- **Extended:** 6000mAh Li-Ion (22.2Wh) - 16 hours
- **Mission Pack:** 12,000mAh Li-Ion (44.4Wh) - 32 hours
- **Solar Charger:** 10W flexible panel (full recharge in 4 hours sun)

---

## Security & COMSEC

### Cryptographic Specifications (NSA Suite B)
- **Encryption:** AES-256-GCM (symmetric), ECDH P-384 (key exchange)
- **Signing:** ECDSA P-384 (digital signatures)
- **Hashing:** SHA-384 (integrity)
- **Key Management:** Type 1 encryption (NSA-certified COMSEC)
- **Zeroization:** Automatic on tamper detect, battery removal, or command

### Access Control
- **Authentication:** CAC/PIV card reader (Common Access Card)
- **Biometric:** Fingerprint scanner (FIPS 201 certified)
- **PIN:** 6-digit alphanumeric + timeout (2 min)
- **Failed Attempts:** 3 failed → lockout → supervisor unlock required
- **Role-Based Access:** Commander, squad leader, rifleman, medic profiles

### Anti-Tamper & Intrusion Detection
- **Tamper Mesh:** Conductive grid on PCB (breaks circuit if opened)
- **Accelerometer:** Detects forced entry, drop events
- **Epoxy Potting:** Critical components encapsulated (crypto module)
- **Self-Destruct:** Zeroize crypto keys on tamper (irreversible)

### Secure Boot & Firmware
- **Boot Chain:** UEFI Secure Boot with NSA-approved bootloader
- **Firmware Signing:** Ed25519 signatures (only signed firmware accepted)
- **TPM 2.0:** Trusted Platform Module (measured boot)
- **BIOS Lock:** Firmware update requires physical jumper + CAC card

---

## Bill of Materials (Military-Specific Components)

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| SAASM GPS | ZED-F9P-SAASM | u-blox | 1 | $485.00 | $485.00 |
| SINCGARS Radio | AN/PRC-154 (OEM) | Harris/L3 | 1 | $2,850.00 | $2,850.00 |
| Thermal Camera | Lepton 3.5 | FLIR | 1 | $250.00 | $250.00 |
| Radiation Detector | SBM-20 GM Tube | DIY Geiger | 1 | $15.00 | $15.00 |
| Chemical Sensor | MQ Series (6x) | Winsen | 6 | $8.50 | $51.00 |
| CAC Card Reader | SCR3500 | Identiv | 1 | $45.00 | $45.00 |
| Ruggedized Case | 6061-T6 Aluminum | Custom | 1 | $120.00 | $120.00 |
| MIL Connectors | MS3116/MS3120 | Glenair | 4 | $25.00 | $100.00 |
| Tamper Mesh | Conductive Grid | Custom | 1 | $30.00 | $30.00 |
| Gen 3+ NV Sensor | CMOS Night Vision | Photonis | 1 | $380.00 | $380.00 |
| Laser Warning | 4-quadrant | Custom | 1 | $150.00 | $150.00 |
| RF Detector | HackRF One (OEM) | Great Scott | 1 | $350.00 | $350.00 |
| **Subtotal (Military Components)** | | | | | **$4,826.00** |

*Note: SINCGARS radio is export-controlled and requires end-user certificate. Add base Pip-Boy cost ($85-$110) for total unit cost.*

---

## Software Integration

### Firmware Components
- **SINCGARS Driver:** Frequency hopping, ECCM, COMSEC keying
- **BFT Protocol:** Blue force tracking (Iridium SATCOM uplink)
- **ATAK Plugin:** Android Tactical Assault Kit integration
- **FBCB2 Interface:** Force XXI Battle Command (UDP/TCP)
- **SALUTE Parser:** Voice-to-text intelligence report generation

### Project-AI Integration
- **Voice Commands:** "Request fire mission", "Report SALUTE", "Check blue force"
- **Mission Planning:** AI-assisted route planning (terrain analysis)
- **Threat Assessment:** Pattern recognition (IED indicators, ambush sites)
- **Language Translation:** 45+ languages (local population engagement)
- **Medical Triage:** Casualty assessment, treatment recommendations

### Machine Learning Features
- **Threat Detection:** Computer vision (weapons, vehicles, IEDs)
- **Predictive Maintenance:** Equipment failure prediction
- **Acoustic Classification:** Gunshot type identification (AK-47, M4, PKM)
- **Biometric Recognition:** Face recognition (HIIDE-compatible)

---

## Compliance & Certifications

### Military Standards
- **MIL-STD-810H:** Environmental engineering (28 test methods)
- **MIL-STD-461G:** EMC requirements for the control of electromagnetic interference
- **MIL-STD-1553:** Data bus (avionics, vehicle integration)
- **MIL-STD-882E:** System safety (hazard analysis, risk assessment)

### Information Assurance
- **NIST SP 800-53:** Security controls (moderate/high baseline)
- **DIACAP/RMF:** DoD Information Assurance Certification and Accreditation
- **FIPS 140-2:** Cryptographic Module Validation (Level 2/3)
- **Common Criteria:** EAL4+ (Evaluation Assurance Level)

### Export Control
- **ITAR:** International Traffic in Arms Regulations (Category XI)
- **EAR:** Export Administration Regulations (ECCN 5A992)
- **COCOM:** Coordinating Committee clearance required for transfer

---

## Usage Examples

### Example 1: Patrol Mission
```
1. Squad leader uploads patrol route waypoints (MGRS coordinates)
2. BFT shows friendly positions (squad members + nearby units)
3. Thermal camera scans for heat signatures (people, vehicles)
4. RF detector alerts to cell phone signal (potential IED trigger)
5. Acoustic sensor detects gunfire (direction + distance calculated)
6. Automatic SALUTE report generated (voice-to-text)
7. Blue force tracking updates command (real-time position)
8. Casualty evacuation coordinates sent to medevac
```

### Example 2: CBRN Threat Response
```
1. Radiation detector alarms (0.5 mSv/h detected)
2. GPS position tagged, alert sent to higher command
3. Chemical sensors activated (scanning for nerve agents)
4. Project-AI provides donning instructions (MOPP gear)
5. Safe route calculated (avoid contaminated area)
6. CBRN report uploaded to NBC-1 database
7. Decontamination procedures displayed on screen
```

### Example 3: Fire Support Coordination
```
1. Spotter identifies target (building, coordinates via laser rangefinder)
2. Voice command: "Request fire mission, building, MGRS 12345 67890"
3. Target coordinates sent to fire direction center (encrypted)
4. Project-AI calculates danger-close distance (safety check)
5. Fire mission approved (artillery coordinates displayed)
6. Impact time countdown displayed (time to take cover)
7. BDA (Battle Damage Assessment) photo captured post-strike
```

---

## Maintenance & Support

### Field Maintenance
- **PMCS:** Preventive Maintenance Checks and Services (daily/weekly/monthly)
- **BII:** Basic Issue Items (cleaning kit, spare battery, antenna)
- **Tools Required:** Torx T6/T8, hex key set, multimeter
- **Repair Parts:** Common components (battery, connectors, seals)

### Depot-Level Repair
- **COMSEC Repair:** Requires COMSEC custodian certification
- **Calibration:** Annual GPS/compass calibration (metrology lab)
- **Component Replacement:** Modular design (swap RF board, display, etc.)

### Logistics
- **NSN:** National Stock Number (assigned upon fielding)
- **Supply Chain:** Defense Logistics Agency (DLA) sourcing
- **MTBF:** Mean Time Between Failures (10,000 hours)
- **MTTR:** Mean Time To Repair (< 30 minutes, unit level)

---

## Training & Doctrine

### Operator Training (40 hours)
1. **Basic Operation:** Power on/off, menu navigation, settings
2. **GPS Navigation:** Waypoint entry, route following, MGRS coordinates
3. **Radio Operation:** Channel selection, encryption fill, troubleshooting
4. **BFT Usage:** Blue force tracking, position reporting, messaging
5. **CBRN Detection:** Sensor interpretation, protective measures
6. **Mission Planning:** Route planning, graphics overlay, target coordination
7. **Troubleshooting:** Common failures, field repairs, diagnostics

### Maintainer Training (80 hours)
1. **Disassembly/Assembly:** Component identification, removal/installation
2. **Diagnostics:** Built-in test (BIT), fault isolation
3. **COMSEC Procedures:** Crypto fill, zeroization, key management
4. **Calibration:** GPS, compass, sensors
5. **Repair:** Component replacement, soldering, sealing

### Doctrine Integration
- **FM 3-0:** Operations (maneuver, fires, intelligence)
- **FM 6-02:** Signal Support (communications, networks)
- **ATP 3-09.50:** Fires (call for fire, target acquisition)
- **FM 4-02.51:** Combat Casualty Care (medical procedures)

---

## Appendix A: SINCGARS Frequency Plan

### VHF-FM Channels (30-87.975 MHz)
| Band | Frequency Range | Channels | Usage |
|------|----------------|----------|-------|
| Low | 30.000-39.975 | 400 | Long-range, day |
| Mid | 40.000-55.975 | 640 | Standard tactical |
| High | 56.000-87.975 | 1280 | Short-range, night |

### Frequency Hopping
- **Hop Rate:** 111 hops/second (slow), 10 hops/second (fast)
- **Hop Set:** Pseudorandom sequence (synchronized with squad)
- **TRANSEC:** Transmission Security (prevents intercept/jamming)
- **Late Net Entry:** Join encrypted network mid-hop (automatic)

---

## Appendix B: Blue Force Tracking Data Format

### Position Report (30-second updates)
```json
{
  "unit_id": "A/1-504 PIR",
  "callsign": "STEEL 6",
  "timestamp": "2026-02-22T09:30:45Z",
  "position": {
    "mgrs": "18S UJ 12345 67890",
    "lat": 35.123456,
    "lon": -78.987654,
    "alt": 125.5
  },
  "status": "GREEN",
  "speed": 15.2,
  "heading": 270,
  "fuel": 75,
  "ammo": 100,
  "personnel": 9,
  "signature": "3045022100..."
}
```

---

## Appendix C: CBRN Detection Thresholds

### Radiation Levels (mSv/h)
| Level | Dose Rate | Action |
|-------|-----------|--------|
| Background | 0.001-0.01 | Normal |
| Elevated | 0.01-0.1 | Monitor |
| Warning | 0.1-1.0 | Don protective gear |
| Danger | 1.0-10.0 | Evacuate immediately |
| Lethal | >10.0 | Emergency MEDEVAC |

### Chemical Agents (ppm)
| Agent | Type | Threshold | Symptoms |
|-------|------|-----------|----------|
| GB (Sarin) | Nerve | 0.0001 | Miosis, respiratory distress |
| VX | Nerve | 0.00001 | Convulsions, paralysis |
| HD (Mustard) | Blister | 0.003 | Blisters, burns |
| CG (Phosgene) | Blood | 3.0 | Pulmonary edema |

---

**Document Version:** 1.0.0  
**Hardware Revision:** A  
**Classification:** UNCLASSIFIED // FOUO  
**Export Control:** ITAR Category XI  
**Last Review:** 2026-02-22  

**RESTRICTED TO AUTHORIZED MILITARY PERSONNEL**  
**DESTROY BY BURNING OR SHREDDING WHEN NO LONGER NEEDED**
