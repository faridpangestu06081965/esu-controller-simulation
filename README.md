# High-Frequency Electrosurgical Unit (ESU) Controller Simulation

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![PyQtGraph](https://img.shields.io/badge/Oscilloscope-PyQtGraph-cyan.svg)
![Domain](https://img.shields.io/badge/Domain-Biomedical--Instrumentation-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An industrial-grade **Biomedical Software Simulation** modeling a high-frequency (470 kHz) **Electrosurgical Unit (ESU)** radiofrequency generator, real-time closed-loop tissue impedance feedback, and patient safety interlock systems.

---

## 📌 Key Features & Engineering Highlights

- ⚡ **470 kHz RF Waveform Generation**:
  - **Pure Cut**: High-frequency continuous sine wave for precise cellular vaporization.
  - **Blend Cut**: Modulated RF pulse bursts for simultaneous cutting and hemostasis.
  - **Fulguration Coagulation**: High-voltage, high-crest-factor interrupted bursts for non-contact coagulation.
- 🔄 **Closed-Loop Impedance Feedback $Z(t)$ & Auto-Tuning**:
  - Real-time tissue desiccation dynamics modeling.
  - Automatic RF power throttling when tissue impedance surges ($>1000\ \Omega$) to prevent charring and excessive thermal necrosis.
- 🛡️ **Patient Safety Interlock (REM - Return Electrode Monitoring)**:
  - Continuous monitoring of neutral pad contact impedance ($20\text{--}130\ \Omega$).
  - Automatic interlock trigger and instant RF shutdown when impedance exceeds $120\ \Omega$ to protect patients from secondary site burns.
- 📊 **60 FPS Real-Time Medical Console**:
  - High-performance dark-themed UI built with PyQt6 and PyQtGraph.
  - High-speed oscilloscope for RF output voltage and live telemetry tracking ($V_{\text{peak}}$, $I_{\text{rms}}$, Tissue $Z$, and Thermal state).

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Plotting / Oscilloscope**: PyQtGraph
- **Numerical Processing**: NumPy

---

## 🎮 Controls & Operating Modes

| Control Component | Function |
| :--- | :--- |
| **Operational Mode Radio** | Switch between Pure Cut, Blend Cut, and Fulguration Coagulation |
| **Power Setpoint Sliders** | Adjust target cutting (10–300 W) and coagulation (5–120 W) power |
| **Activated Cut Pedal** | Hold Yellow Pedal button to engage RF Cutting mode |
| **Activated Coag Pedal** | Hold Blue Pedal button to engage RF Coagulation mode |
| **REM Circuit Test Slider** | Test Patient Return Electrode contact impedance safety limits |

---

## 🚀 Quick Start

```bash
pip install PyQt6 pyqtgraph numpy
python esu_controller_sim.py
