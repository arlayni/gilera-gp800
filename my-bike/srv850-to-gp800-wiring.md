# SRV850 ECU to GP800 Wiring Integration

**Status:** NOT YET DOCUMENTED

This document is a stub for documenting the electrical integration of the Aprilia SRV850 ECU into the Gilera GP800 chassis.

## Investigation Checklist

The following topics need to be researched and documented:

### ECU Pinout Comparison
- [ ] Map SRV850 ECU connector pins to function
- [ ] Map GP800 original ECU connector pins to function
- [ ] Identify pin-to-pin differences between SRV850 and GP800
- [ ] Document any adapters or rewiring used during installation

### Sensor Wiring
- [ ] Throttle Position Sensor (TPS) — voltage divider, common wire
- [ ] Engine Coolant Temperature (ECT) — thermistor, reference voltage
- [ ] Intake Air Temperature (IAT) — thermistor, reference voltage
- [ ] Manifold Absolute Pressure (MAP) — sensor reference, signal ground
- [ ] Oxygen sensor (lambda) — heater circuit, signal wire
- [ ] Crankshaft position (CPS) — pickup coil, shielding

### Ignition & Fuel Control
- [ ] Ignition coil power and signal wires
- [ ] Fuel injector power and pulse signal
- [ ] Fuel pump relay control
- [ ] Idle control stepper or solenoid (if present)

### ABS Module Integration (SRV850 Specific)
- [ ] ABS pump motor control (if wired)
- [ ] Wheel speed sensor wires (front/rear)
- [ ] ABS modulator solenoid signals
- [ ] Brake pressure switch integration
- [ ] Dashboard/gauge cluster communication for ABS lamp

### Accessory Circuits
- [ ] Side-stand switch (safety interlock)
- [ ] Clutch switch (if present)
- [ ] Start button circuit
- [ ] Dashboard communication bus (if KWP2000/ISO9141)
- [ ] Gauge cluster connector pins

### Power & Ground Distribution
- [ ] Main battery positive wire (size, routing)
- [ ] Ground connections (engine block, frame, battery negative)
- [ ] Relay base power and ground
- [ ] Main fuse rating and location

## Next Steps

1. Obtain wiring diagrams for:
   - Aprilia SRV850 (OEM service manual or parts diagram)
   - Gilera GP800 (OEM service manual)
2. Physically trace wiring harness connections
3. Compare pinouts and document any discrepancies
4. Identify any loose, damaged, or suspect connectors
5. Create detailed wiring comparison table (proposed format below)

## Proposed Wiring Comparison Table

| Function | GP800 Signal | SRV850 Signal | Actual Wire Color | Status |
|----------|--------------|---------------|-------------------|--------|
| ECU Pin 1 | ? | ? | ? | ? |
| ECU Pin 2 | ? | ? | ? | ? |
| ... | ... | ... | ... | ... |

---

*This stub should be expanded with actual measurements and traced wiring as investigation proceeds.*
