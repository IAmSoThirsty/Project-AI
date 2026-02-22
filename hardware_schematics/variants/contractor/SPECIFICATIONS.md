# Contractor Variant - Technical Specifications

**Variant:** Contractor  
**Version:** 1.0.0  
**Last Updated:** 2026-02-22  
**Status:** Production-Ready  
**Target Audience:** General Contractors, Construction Workers, Home Improvement Professionals, Project Managers, Electricians, Plumbers, HVAC Technicians

---

## Overview

The Contractor variant is designed for construction, renovation, home improvement, trade work, and project management. It provides measurement tools, level/plumb detection, material calculators, blueprint viewing, job costing, code compliance, safety monitoring, and client communication while maintaining durability for harsh construction environments.

---

## Domain-Specific Features

### 1. Digital Measurement & Layout Tools
- **Laser Distance Meter:** 0.05-100m range (±1.5mm accuracy, Bosch GLM 100C compatible)
- **Laser Level:** Virtual level overlay on camera (bubble level + cross-hair)
- **Digital Angle Finder:** Protractor mode (0-360°, ±0.1° accuracy)
- **Area Calculator:** Length × width = square footage/meters
- **Volume Calculator:** For concrete, gravel, mulch orders
- **Stud Finder:** Metal detector + density sensor (locate studs, pipes, wires)
- **Pitch/Slope:** Roof pitch calculator (rise/run, degrees, percent)
- **Unit Converter:** Imperial ↔ Metric (feet/inches ↔ meters/cm)

### 2. Blueprint & CAD Viewer
- **File Formats:** PDF, DWG, DXF, Revit (IFC), SketchUp
- **Zoom & Pan:** Multi-touch gestures, pinch-to-zoom
- **Layers:** Toggle visibility of electrical, plumbing, HVAC, structural layers
- **Measurements:** On-screen measuring tool (calibrate to scale)
- **Annotations:** Markup with stylus (notes, dimensions, change orders)
- **3D Viewer:** Rotate 3D models (BIM - Building Information Modeling)
- **Cloud Sync:** Dropbox, Google Drive, Procore, PlanGrid integration
- **Version Control:** Track blueprint revisions, compare versions

### 3. Material & Cost Estimating
- **Material Calculators:** Drywall sheets, lumber (board feet), roofing shingles, flooring, paint
- **Waste Factor:** Auto-add 10-15% overage for cuts/waste
- **Price Database:** Home Depot, Lowe's, local lumber yard pricing (API integration)
- **Labor Estimating:** Hours × rate per task (framing, drywall, electrical, etc.)
- **Job Costing:** Track actual costs vs estimates
- **Invoicing:** Generate invoices with itemized materials + labor
- **Profit Margin:** Calculate markup (materials + labor + overhead + profit)

### 4. Level, Plumb & Square Detection
- **3-Axis Accelerometer:** Detect level (0° horizontal) and plumb (90° vertical)
- **Visual Overlay:** Camera viewfinder with level bubble, cross-hair
- **Audible Feedback:** Beep when level achieved
- **Calibration:** User-calibratable against known level surface
- **Pitch Display:** Roof slope in degrees, percent, or rise/run (12/12, etc.)
- **Square Check:** 3-4-5 triangle calculator (Pythagorean theorem)

### 5. Code Compliance & Safety
- **Building Codes:** ICC (International Code Council) database - IBC, IRC, NEC, IPC, IMC
- **Lookup by Location:** Auto-detect city/county, show local amendments
- **Electrical Code:** NEC (National Electrical Code) - wire sizing, breaker sizing, GFCI/AFCI requirements
- **Plumbing Code:** IPC/UPC - pipe sizing, vent sizing, trap requirements
- **Safety Standards:** OSHA regulations (fall protection, PPE, trenching, scaffolding)
- **Permit Requirements:** What requires permits in local jurisdiction
- **Inspection Checklists:** Pre-inspection prep, common deficiencies

### 6. Tool Inventory & Maintenance
- **Tool Database:** Catalog all tools (make, model, serial number, purchase date)
- **Barcode Scanner:** Track tool locations, check-in/check-out
- **Maintenance Reminders:** Oil changes, blade sharpening, calibration
- **Rental Tracking:** Track rented equipment (return dates, costs)
- **Replacement Costs:** Insurance documentation for theft/loss
- **User Manuals:** Store PDF manuals for tools, equipment

### 7. Job Site Communication
- **Team Messaging:** Group chats with crew (foreman, subs, laborers)
- **Photo Documentation:** Progress photos with GPS, timestamp, annotations
- **Voice Memos:** Quick notes to self, crew instructions
- **Client Updates:** Send progress photos, status updates via email/SMS
- **Video Calls:** FaceTime, Zoom for remote client walkthroughs
- **RFI (Request for Information):** Track questions to architect/engineer
- **Change Orders:** Document scope changes, get client approval

### 8. Jobsite Safety & Environmental Monitoring
- **Sound Level Meter:** OSHA noise limits (85 dB TWA, 90 dB action level)
- **Gas Detector:** CO, natural gas, propane (combustible gas detector)
- **Air Quality:** Particulate matter (PM2.5, PM10) - dust, fumes
- **Heat Stress:** WBGT (Wet Bulb Globe Temperature) for outdoor work
- **Weather Alerts:** Lightning, severe weather, wind speed warnings
- **Fall Hazard:** Detect working at heights, prompt for fall protection

### 9. Time Tracking & Job Management
- **Clock In/Out:** GPS-verified time tracking (prevent buddy punching)
- **Task Assignment:** Assign tasks to crew members
- **Daily Reports:** Auto-generate daily work reports
- **Equipment Hours:** Track machine hours (excavator, skid steer, etc.)
- **Timesheet Export:** Export to QuickBooks, ADP, Gusto payroll
- **Integration:** Procore, CoConstruct, Buildertrend, Fieldwire

### 10. Electrical Testing (Optional Module)
- **Multimeter:** AC/DC voltage, current, resistance, continuity
- **Non-Contact Voltage Tester:** Detect live wires (50-1000V AC)
- **GFCI Tester:** Test ground fault circuit interrupters
- **Outlet Tester:** Wiring verification (correct/open ground/reversed polarity)
- **Circuit Tracer:** Identify circuit breakers for outlets/lights

---

## Hardware Specifications

### Ruggedization (Construction Environment)
- **Drop Resistance:** MIL-STD-810H (2m drops onto concrete - 6.5ft)
- **Water/Dust:** IP68 (1.5m submersion, dust-tight, sawdust resistant)
- **Temperature:** -20°C to 60°C operating range
- **Impact Protection:** Reinforced rubber corners, raised bezel (screen protection)
- **Case Material:** High-impact polycarbonate + TPU shock absorption
- **Screen:** Gorilla Glass 6 + anti-scratch coating, glove-friendly touch

### Additional Sensors (Contractor-Specific)
- **Laser Rangefinder:** Time-of-flight sensor (100m range, ±1.5mm)
- **Magnetometer:** Detect ferrous metal (studs, rebar, nails)
- **Sound Level Meter:** MEMS microphone calibrated for dB(A) weighting
- **Gas Sensors:** MQ-2 (combustible gas), MQ-7 (CO)
- **Barometer:** Altitude/elevation (useful for foundation/grading work)

### Expansion Modules
- **Slot 1:** Laser measurement module (distance, area, volume)
- **Slot 2:** Stud finder/metal detector module
- **Slot 3:** Electrical testing module (multimeter, GFCI tester)
- **Slot 4:** Thermal imaging camera (detect heat loss, moisture)

### Connector Panel (Ruggedized, IP68 Sealed)
```
┌────────────────────────────────────┐
│  [Sealed USB-C] [Sealed Audio]     │  Data & Headphone
│  [Laser Rangefinder Port]          │  External Sensor
│  [CAT III Probe Jacks]             │  Electrical Testing (optional)
│  [External Antenna] (GPS)          │  Jobsite Location
└────────────────────────────────────┘
```

### Power Budget (Contractor Variant)
- **Idle:** 2.5W (display on, GPS active)
- **Laser Measurement:** +0.8W (laser rangefinder active)
- **Blueprint Viewing:** +0.5W (PDF rendering)
- **Electrical Testing:** +1.2W (multimeter circuits active)
- **Maximum Load:** 5.0W (all systems active)
- **Battery Life:** 10-18 hours (full work day + overtime)

---

## Bill of Materials (Contractor-Specific Components)

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| Laser Rangefinder | VL53L1X | STMicroelectronics | 1 | $12.50 | $12.50 |
| Magnetometer | MLX90393 | Melexis | 1 | $4.50 | $4.50 |
| Sound Level Mic | ICS-43434 | InvenSense | 1 | $2.80 | $2.80 |
| Gas Sensor (MQ-2) | MQ-2 | Winsen | 1 | $3.50 | $3.50 |
| Gas Sensor (MQ-7) | MQ-7 | Winsen | 1 | $5.00 | $5.00 |
| Ruggedized Case | Custom TPU/PC | N/A | 1 | $45.00 | $45.00 |
| Screen Protector | Tempered Glass | Generic | 1 | $8.00 | $8.00 |
| **Subtotal (Contractor Components)** | | | | | **$81.30** |

*Optional Electrical Testing Module:*

| Component | Part Number | Supplier | Qty | Unit Price | Total |
|-----------|-------------|----------|-----|------------|-------|
| 24-bit ADC | ADS1256 | TI | 1 | $18.00 | $18.00 |
| Voltage Divider Network | Custom PCB | N/A | 1 | $12.00 | $12.00 |
| Current Shunt | 0.1Ω 2W | Vishay | 1 | $3.50 | $3.50 |
| CAT III Probe Jacks | 4mm Banana | Pomona | 2 | $4.50 | $9.00 |
| **Subtotal (Electrical Module)** | | | | | **$42.50** |

**Total Contractor Variant Cost:**
- Base + Contractor: $166.30-$191.30
- With Electrical Module: $208.80-$233.80

---

## Software Integration

### Firmware Components
- **CAD Renderer:** LibreCAD engine for DWG/DXF
- **PDF Viewer:** MuPDF (fast rendering)
- **Material Calculator:** Custom algorithms (board feet, shingles, etc.)
- **Code Database:** Offline cache of ICC building codes
- **Time Tracker:** GPS-verified clock in/out

### Project-AI Integration
- **Voice Commands:** "Measure distance to wall", "Calculate drywall for 12x15 room", "Look up NEC wire sizing for 50 amp circuit"
- **Blueprint Analysis:** AI identifies rooms, counts windows/doors, estimates materials
- **Code Lookup:** "What's the minimum R-value for attic insulation in my area?"
- **Safety Alerts:** "High CO detected, ventilate area immediately"
- **Job Planning:** AI suggests task sequence, critical path

### Machine Learning Features
- **Defect Detection:** Analyze photos for quality issues (uneven paint, drywall cracks)
- **Progress Tracking:** Compare progress photos to schedule, estimate % complete
- **Cost Prediction:** Predict final job cost based on current burn rate
- **Safety Violations:** Detect missing PPE (hard hat, safety glasses, harness)

---

## Code & Standards Database

### Building Codes
- **IBC:** International Building Code (commercial structures)
- **IRC:** International Residential Code (1-2 family dwellings)
- **IFC:** International Fire Code (fire safety, alarms, sprinklers)
- **IECC:** International Energy Conservation Code (insulation, HVAC efficiency)

### Trade-Specific Codes
- **NEC:** National Electrical Code (NFPA 70)
- **IPC:** International Plumbing Code
- **UPC:** Uniform Plumbing Code (Western US)
- **IMC:** International Mechanical Code (HVAC)

### Safety Standards
- **OSHA 1926:** Construction industry regulations
- **OSHA 1910:** General industry (some overlap with construction)
- **ANSI Z359:** Fall protection standards

---

## Usage Examples

### Example 1: Room Measurement
```
1. Voice command: "Measure room dimensions"
2. Laser rangefinder: Point at wall, trigger measurement
3. Length: 15' 6" (4.72m)
4. Width: 12' 3" (3.73m)
5. Auto-calculate: Area = 190 sq ft (17.6 m²)
6. Ask: "How much flooring needed?"
7. AI: "190 sq ft + 10% waste = 209 sq ft (20 boxes of 10.45 sq ft each)"
8. Pricing: Check Home Depot - $2.50/sq ft = $522.50 total
```

### Example 2: Electrical Code Lookup
```
1. Voice: "What size wire for 50 amp 240V circuit?"
2. AI: "Per NEC Table 310.15(B)(16):"
   - Copper: 6 AWG THHN (75°C rating)
   - Aluminum: 4 AWG (not recommended for residential)
3. Follow-up: "What about conduit size?"
4. AI: "Per NEC Chapter 9, Table 4:"
   - 3 conductors (2 hot + ground) in 1" EMT or 3/4" rigid
5. Log: Save to project notes for inspector
```

### Example 3: Blueprint Markup
```
1. Load blueprint: Floor plan from PlanGrid
2. Client wants to move wall
3. Markup: Draw new wall location with stylus (red line)
4. Measure: New room is now 14' x 12' (was 16' x 10')
5. Note: "Move wall 2ft west - check with engineer (load-bearing?)"
6. Photo: Take picture of existing wall
7. RFI: Send to architect via email (includes markup + photo)
8. Track: Log RFI #12, awaiting response
```

### Example 4: Job Costing
```
Materials:
- Lumber: $2,450
- Drywall: $680
- Electrical: $920
- Plumbing: $1,150
- HVAC: $3,200
Total Materials: $8,400

Labor:
- Framing: 40 hrs × $45/hr = $1,800
- Drywall: 32 hrs × $40/hr = $1,280
- Electrical: 24 hrs × $65/hr = $1,560
- Plumbing: 20 hrs × $60/hr = $1,200
Total Labor: $5,840

Subtotal: $14,240
Overhead (15%): $2,136
Profit (20%): $3,275
Total Bid: $19,651
```

---

## Safety Protocols

### OSHA Fall Protection (1926.501)
- **Trigger Height:** 6 feet (general industry), 4 feet (scaffolds)
- **Systems:** Guardrails, safety nets, personal fall arrest (harness + lanyard)
- **Inspection:** Daily inspection of harnesses, lanyards, anchors

### Electrical Safety
- **Lockout/Tagout:** De-energize circuits before work
- **Arc Flash PPE:** FR clothing for energized work >50V
- **GFCI:** Required for temporary power on construction sites
- **Wet Locations:** Use GFCI-protected outlets

### Confined Space Entry (1926.1200)
- **Permit Required:** Tanks, manholes, crawl spaces with limited access
- **Atmospheric Testing:** O₂, LEL, CO, H₂S before entry
- **Attendant:** Someone outside to monitor, call for rescue

### Trenching & Excavation (1926.650)
- **Protective Systems:** Sloping, benching, shoring, trench box
- **Competent Person:** Inspect daily, after rain, cave-ins
- **Depth Triggers:** 5 feet requires protection, 20 feet requires engineer design

---

## Maintenance & Support

### Recommended Accessories
- **Hard Hat Clip:** Secure device to hard hat for hands-free use
- **Tool Belt Holster:** Quick-access pouch (fits standard tool belt)
- **Magnetic Mount:** Stick to metal studs, electrical panels, toolbox
- **Extended Battery:** 8000mAh for 24+ hour runtime
- **Bluetooth Headset:** Hands-free calls, voice commands (noise-canceling)
- **Portable Charger:** Solar panel or vehicle 12V adapter

### Calibration & Maintenance
- **Laser Rangefinder:** Annual calibration against known distance
- **Level Sensor:** Calibrate against precision level (monthly)
- **Gas Sensors:** Replace annually (electrochemical cells degrade)
- **Protective Case:** Inspect for cracks, replace if damaged

---

## Appendix A: Material Calculators

### Drywall
```
Formula: (Wall Area - Openings) / 32 sq ft per sheet

Example:
Room: 12' × 15' × 8' ceiling height
Wall Area: 2(12×8) + 2(15×8) = 432 sq ft
Openings: 2 doors (21 sq ft each) + 3 windows (15 sq ft each) = 87 sq ft
Net Area: 432 - 87 = 345 sq ft
Sheets: 345 / 32 = 10.8 → 11 sheets (round up)
Plus 10% waste: 11 × 1.1 = 12.1 → 13 sheets
```

### Lumber (Board Feet)
```
Formula: (Thickness in inches × Width in inches × Length in feet) / 12

Example:
2×4×8: (1.5 × 3.5 × 8) / 12 = 3.5 board feet
2×6×12: (1.5 × 5.5 × 12) / 12 = 8.25 board feet
```

### Concrete
```
Formula: Length × Width × Depth / 27 (cubic yards)

Example:
Slab: 20' × 30' × 4" (0.33 feet) thick
Volume: 20 × 30 × 0.33 = 198 cu ft / 27 = 7.3 cu yd
Add 10%: 7.3 × 1.1 = 8.0 cu yd
```

### Roofing Shingles
```
Formula: (Roof Area / 100) × 3 bundles per square

Example:
Roof: 40' × 30' = 1200 sq ft / 100 = 12 squares
Bundles: 12 × 3 = 36 bundles
Add 10%: 36 × 1.1 = 39.6 → 40 bundles
```

---

## Appendix B: Electrical Reference

### NEC Wire Sizing (Copper, 75°C, 60A Max Breaker)
| Breaker | Wire Size | Max Distance (12V Drop @ 240V) |
|---------|-----------|--------------------------------|
| 15A | 14 AWG | 57 feet |
| 20A | 12 AWG | 72 feet |
| 30A | 10 AWG | 90 feet |
| 40A | 8 AWG | 114 feet |
| 50A | 6 AWG | 144 feet |
| 60A | 4 AWG | 181 feet |

### Conduit Fill (NEC Chapter 9, Table 4)
| Conductors | 1/2" EMT | 3/4" EMT | 1" EMT |
|------------|----------|----------|---------|
| 3 × 14 AWG | ✓ | ✓ | ✓ |
| 3 × 12 AWG | ✓ | ✓ | ✓ |
| 3 × 10 AWG | ✗ | ✓ | ✓ |
| 3 × 8 AWG | ✗ | ✗ | ✓ |

---

## Appendix C: Live Translation Integration

### Multi-Language Support for Client Communication
- **Languages:** 45+ languages (Spanish, Mandarin, Portuguese, Vietnamese, Korean, etc.)
- **Use Cases:** Client meetings, homeowner communication, crew instructions
- **Translation Modes:** Real-time speech, text translation, photo translation (signs, labels)
- **Voice Interface:** Speak in English, device translates to client's language via speaker
- **Two-Way:** Client speaks in their language, device translates to English for contractor

**See LIVE_TRANSLATION_MATRIX.md for full integration details**

---

**Document Version:** 1.0.0  
**Hardware Revision:** A  
**Last Review:** 2026-02-22  

**Building Quality, One Project at a Time**  
**Safety First, Quality Always**
