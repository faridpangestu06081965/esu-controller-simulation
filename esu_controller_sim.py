# -*- coding: utf-8 -*-
import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, QGroupBox, 
                             QRadioButton, QFrame, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg

pg.setConfigOption('background', '#0b0f19')
pg.setConfigOption('foreground', '#d0e0f0')

class ESUControllerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGH-FREQUENCY ELECTROSURGICAL UNIT (ESU) - INDUSTRIAL CONSOLE")
        self.resize(1300, 800)

        self.rf_frequency = 470000
        self.sampling_rate = 5000
        self.time_buffer = np.linspace(0, 0.005, self.sampling_rate)
        
        self.is_active = False
        self.mode = "PURE_CUT"
        self.target_power_cut = 100
        self.target_power_coag = 50
        
        self.rem_impedance = 50.0
        self.tissue_impedance = 100.0
        self.tissue_temp = 37.0
        self.time_active_sec = 0.0
        
        self.history_len = 200
        self.hist_time = np.zeros(self.history_len)
        self.hist_impedance = np.full(self.history_len, 100.0)
        self.hist_power = np.zeros(self.history_len)
        self.hist_temp = np.full(self.history_len, 37.0)

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(20)

    def init_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #080c14; color: #e0e8f0; font-family: 'Segoe UI';")
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        header = QFrame()
        header.setStyleSheet("background-color: #121926; border: 1px solid #1a2638; border-radius: 8px;")
        header_layout = QHBoxLayout(header)
        
        title_lbl = QLabel("SURGICAL RF GENERATOR | MODEL ESU-4700 PRO")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #00d2ff;")
        
        self.status_badge = QLabel("SYSTEM READY / STANDBY")
        self.status_badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.status_badge.setStyleSheet("color: #00ff88; background-color: #0a2e1e; padding: 6px 14px; border-radius: 6px;")
        
        self.rem_status = QLabel("REM SAFETY: OK (50 Ohm)")
        self.rem_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.rem_status.setStyleSheet("color: #00e5ff; background-color: #0d2838; padding: 6px 12px; border-radius: 6px;")

        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.rem_status)
        header_layout.addWidget(self.status_badge)
        main_layout.addWidget(header)

        content_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        
        mode_group = QGroupBox("OPERATIONAL MODE")
        mode_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d2ff; border: 1px solid #1a2d42; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        mode_layout = QVBoxLayout(mode_group)
        
        self.radio_cut = QRadioButton("PURE CUT (Continuous RF)")
        self.radio_blend = QRadioButton("BLEND CUT (Modulated RF)")
        self.radio_coag = QRadioButton("FULGURATION COAG (High Crest Factor)")
        self.radio_cut.setChecked(True)
        
        self.radio_cut.toggled.connect(lambda: self.set_mode("PURE_CUT"))
        self.radio_blend.toggled.connect(lambda: self.set_mode("BLEND_1"))
        self.radio_coag.toggled.connect(lambda: self.set_mode("COAG"))
        
        mode_layout.addWidget(self.radio_cut)
        mode_layout.addWidget(self.radio_blend)
        mode_layout.addWidget(self.radio_coag)
        left_panel.addWidget(mode_group)

        power_group = QGroupBox("POWER OUTPUT SETPOINTS")
        power_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d2ff; border: 1px solid #1a2d42; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        power_layout = QGridLayout(power_group)

        power_layout.addWidget(QLabel("CUT POWER:"), 0, 0)
        self.lbl_cut_power = QLabel("100 W")
        self.lbl_cut_power.setStyleSheet("color: #00ff88; font-weight: bold;")
        power_layout.addWidget(self.lbl_cut_power, 0, 1)

        self.slider_cut = QSlider(Qt.Orientation.Horizontal)
        self.slider_cut.setRange(10, 300)
        self.slider_cut.setValue(100)
        self.slider_cut.valueChanged.connect(self.update_power_settings)
        power_layout.addWidget(self.slider_cut, 1, 0, 1, 2)

        power_layout.addWidget(QLabel("COAG POWER:"), 2, 0)
        self.lbl_coag_power = QLabel("50 W")
        self.lbl_coag_power.setStyleSheet("color: #ff2a6d; font-weight: bold;")
        power_layout.addWidget(self.lbl_coag_power, 2, 1)

        self.slider_coag = QSlider(Qt.Orientation.Horizontal)
        self.slider_coag.setRange(5, 120)
        self.slider_coag.setValue(50)
        self.slider_coag.valueChanged.connect(self.update_power_settings)
        power_layout.addWidget(self.slider_coag, 3, 0, 1, 2)

        left_panel.addWidget(power_group)

        safety_group = QGroupBox("PATIENT REM CIRCUIT TEST")
        safety_group.setStyleSheet("QGroupBox { font-weight: bold; color: #00d2ff; border: 1px solid #1a2d42; border-radius: 6px; margin-top: 10px; padding-top: 10px; }")
        safety_layout = QVBoxLayout(safety_group)
        
        self.lbl_rem_val = QLabel("Neutral Plate Contact: 50 Ohm")
        safety_layout.addWidget(self.lbl_rem_val)
        
        self.slider_rem = QSlider(Qt.Orientation.Horizontal)
        self.slider_rem.setRange(20, 160)
        self.slider_rem.setValue(50)
        self.slider_rem.valueChanged.connect(self.update_rem)
        safety_layout.addWidget(self.slider_rem)
        
        left_panel.addWidget(safety_group)

        self.btn_cut = QPushButton("ACTIVATED CUT (YELLOW PEDAL)")
        self.btn_cut.setStyleSheet("""
            QPushButton { background-color: #2e2400; color: #ffcc00; font-weight: bold; font-size: 13px; border: 2px solid #ffcc00; padding: 12px; border-radius: 6px; }
            QPushButton:pressed { background-color: #ffcc00; color: #000000; }
        """)
        self.btn_cut.pressed.connect(self.start_cut)
        self.btn_cut.released.connect(self.stop_rf)

        self.btn_coag = QPushButton("ACTIVATED COAG (BLUE PEDAL)")
        self.btn_coag.setStyleSheet("""
            QPushButton { background-color: #001a33; color: #0099ff; font-weight: bold; font-size: 13px; border: 2px solid #0099ff; padding: 12px; border-radius: 6px; }
            QPushButton:pressed { background-color: #0099ff; color: #ffffff; }
        """)
        self.btn_coag.pressed.connect(self.start_coag)
        self.btn_coag.released.connect(self.stop_rf)

        left_panel.addWidget(self.btn_cut)
        left_panel.addWidget(self.btn_coag)
        left_panel.addStretch()

        content_layout.addLayout(left_panel, stretch=1)

        right_panel = QVBoxLayout()

        self.plot_rf = pg.PlotWidget(title="<b>RF VOLTAGE WAVEFORM OUTPUT (470 kHz)</b>")
        self.plot_rf.setYRange(-400, 400)
        self.plot_rf.showGrid(x=True, y=True, alpha=0.3)
        self.curve_rf = self.plot_rf.plot(pen=pg.mkPen('#00ff88', width=1.5))
        right_panel.addWidget(self.plot_rf)

        self.plot_telemetry = pg.PlotWidget(title="<b>TISSUE IMPEDANCE Z(t) & DELIVERED POWER P(t)</b>")
        self.plot_telemetry.showGrid(x=True, y=True, alpha=0.3)
        
        self.curve_imp = self.plot_telemetry.plot(pen=pg.mkPen('#ff2a6d', width=2), name="Impedance (Ohm)")
        self.curve_pwr = self.plot_telemetry.plot(pen=pg.mkPen('#00d2ff', width=2), name="Power (W)")
        right_panel.addWidget(self.plot_telemetry)

        content_layout.addLayout(right_panel, stretch=3)
        main_layout.addLayout(content_layout)

        footer = QFrame()
        footer.setStyleSheet("background-color: #121926; border: 1px solid #1a2638; border-radius: 6px; padding: 4px;")
        footer_layout = QHBoxLayout(footer)

        self.lbl_tele_v = QLabel("V_peak: 0 V")
        self.lbl_tele_i = QLabel("I_rms: 0.00 A")
        self.lbl_tele_z = QLabel("Tissue Z: 100.0 Ohm")
        self.lbl_tele_temp = QLabel("Tissue Temp: 37.0 \u00b0C")

        for lbl in [self.lbl_tele_v, self.lbl_tele_i, self.lbl_tele_z, self.lbl_tele_temp]:
            lbl.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #90a4ae;")
            footer_layout.addWidget(lbl)

        main_layout.addWidget(footer)

    def set_mode(self, mode):
        self.mode = mode

    def update_power_settings(self):
        self.target_power_cut = self.slider_cut.value()
        self.target_power_coag = self.slider_coag.value()
        self.lbl_cut_power.setText(f"{self.target_power_cut} W")
        self.lbl_coag_power.setText(f"{self.target_power_coag} W")

    def update_rem(self):
        self.rem_impedance = self.slider_rem.value()
        self.lbl_rem_val.setText(f"Neutral Plate Contact: {self.rem_impedance} Ohm")
        if self.rem_impedance > 120:
            self.rem_status.setText(f"REM FAULT: HIGH IMPEDANCE ({self.rem_impedance} Ohm)")
            self.rem_status.setStyleSheet("color: #ffffff; background-color: #ff0055; padding: 6px 12px; border-radius: 6px;")
            self.stop_rf()
        else:
            self.rem_status.setText(f"REM SAFETY: OK ({self.rem_impedance} Ohm)")
            self.rem_status.setStyleSheet("color: #00e5ff; background-color: #0d2838; padding: 6px 12px; border-radius: 6px;")

    def start_cut(self):
        if self.rem_impedance > 120:
            return
        self.is_active = True
        self.status_badge.setText("ACTIVE - RF CUTTING ENGAGED")
        self.status_badge.setStyleSheet("color: #000000; background-color: #ffcc00; padding: 6px 14px; border-radius: 6px;")

    def start_coag(self):
        if self.rem_impedance > 120:
            return
        self.is_active = True
        self.status_badge.setText("ACTIVE - RF COAGULATION ENGAGED")
        self.status_badge.setStyleSheet("color: #ffffff; background-color: #0099ff; padding: 6px 14px; border-radius: 6px;")

    def stop_rf(self):
        self.is_active = False
        self.time_active_sec = 0.0
        self.tissue_impedance = 100.0
        self.tissue_temp = 37.0
        if self.rem_impedance <= 120:
            self.status_badge.setText("SYSTEM READY / STANDBY")
            self.status_badge.setStyleSheet("color: #00ff88; background-color: #0a2e1e; padding: 6px 14px; border-radius: 6px;")

    def update_simulation(self):
        if self.is_active:
            self.time_active_sec += 0.02
            
            if self.time_active_sec < 0.5:
                self.tissue_impedance = 100.0 - (self.time_active_sec * 30.0)
            else:
                self.tissue_impedance += (self.time_active_sec ** 2.2) * 18.0

            self.tissue_temp = min(120.0, 37.0 + (self.time_active_sec * 35.0))
            p_set = self.target_power_cut if "CUT" in self.status_badge.text() else self.target_power_coag
            
            if self.tissue_impedance > 1000.0:
                delivered_power = p_set * (1000.0 / self.tissue_impedance)
            else:
                delivered_power = p_set

            v_peak = np.sqrt(2 * delivered_power * self.tissue_impedance)
            i_rms = np.sqrt(delivered_power / max(1.0, self.tissue_impedance))

            if self.mode == "PURE_CUT":
                waveform = v_peak * np.sin(2 * np.pi * 50 * self.time_buffer)
            elif self.mode == "BLEND_1":
                envelope = np.where((self.time_buffer * 1000) % 2 < 1, 1.0, 0.1)
                waveform = v_peak * np.sin(2 * np.pi * 50 * self.time_buffer) * envelope
            else:
                envelope = np.where((self.time_buffer * 1000) % 5 < 0.8, np.exp(-((self.time_buffer * 1000) % 5) * 4), 0.0)
                waveform = v_peak * 2.2 * np.sin(2 * np.pi * 50 * self.time_buffer) * envelope

            self.lbl_tele_v.setText(f"V_peak: {v_peak:.1f} V")
            self.lbl_tele_i.setText(f"I_rms: {i_rms:.2f} A")
            self.lbl_tele_z.setText(f"Tissue Z: {self.tissue_impedance:.1f} Ohm")
            self.lbl_tele_temp.setText(f"Tissue Temp: {self.tissue_temp:.1f} \u00b0C")

        else:
            waveform = np.zeros_like(self.time_buffer)
            delivered_power = 0.0
            self.lbl_tele_v.setText("V_peak: 0 V")
            self.lbl_tele_i.setText("I_rms: 0.00 A")
            self.lbl_tele_z.setText("Tissue Z: RESTING")
            self.lbl_tele_temp.setText("Tissue Temp: 37.0 \u00b0C")

        self.curve_rf.setData(waveform)

        self.hist_impedance = np.roll(self.hist_impedance, -1)
        self.hist_power = np.roll(self.hist_power, -1)
        self.hist_impedance[-1] = self.tissue_impedance if self.is_active else 100.0
        self.hist_power[-1] = delivered_power

        self.curve_imp.setData(self.hist_impedance)
        self.curve_pwr.setData(self.hist_power)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ESUControllerApp()
    window.show()
    sys.exit(app.exec())
