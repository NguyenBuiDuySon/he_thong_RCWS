from __future__ import annotations

from pathlib import Path

import yaml
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig, load_config


class SetupSection(QFrame):
    def __init__(
        self,
        title: str,
    ) -> None:
        super().__init__()

        self.setProperty(
            "setupSection",
            True,
        )

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        self._grid.setHorizontalSpacing(16)
        self._grid.setVerticalSpacing(10)

        title_label = QLabel(title)
        title_label.setProperty(
            "setupSectionTitle",
            True,
        )

        self._grid.addWidget(
            title_label,
            0,
            0,
            1,
            2,
        )

        self._row = 1

        self._grid.setColumnStretch(
            0,
            2,
        )

        self._grid.setColumnStretch(
            1,
            3,
        )

    def add_row(
        self,
        label: str,
        widget: QWidget,
    ) -> None:
        name_label = QLabel(label)
        name_label.setProperty(
            "setupKey",
            True,
        )

        widget.setMinimumHeight(38)

        self._grid.addWidget(
            name_label,
            self._row,
            0,
        )

        self._grid.addWidget(
            widget,
            self._row,
            1,
        )

        self._row += 1


class SetupPage(QWidget):
    def __init__(
        self,
        config: AppConfig,
    ) -> None:
        super().__init__()

        self._config = config
        self._config_path = Path("configs/default.yaml")

        root = QVBoxLayout(self)

        root.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        root.setSpacing(12)

        title = QLabel("SETUP")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Cấu hình thiết bị và giao tiếp hệ thống")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

        dashboard = QGridLayout()

        dashboard.setHorizontalSpacing(10)
        dashboard.setVerticalSpacing(10)

        self.camera_section = SetupSection("CAMERA")

        self.camera_source = QLineEdit()

        self.camera_width = QSpinBox()
        self.camera_width.setRange(
            160,
            7680,
        )

        self.camera_height = QSpinBox()
        self.camera_height.setRange(
            120,
            4320,
        )

        self.camera_fps = QSpinBox()
        self.camera_fps.setRange(
            1,
            240,
        )

        self.camera_backend = QComboBox()

        self.camera_backend.addItems(
            [
                "auto",
                "dshow",
                "msmf",
            ]
        )

        self.camera_section.add_row(
            "Source",
            self.camera_source,
        )

        self.camera_section.add_row(
            "Width",
            self.camera_width,
        )

        self.camera_section.add_row(
            "Height",
            self.camera_height,
        )

        self.camera_section.add_row(
            "FPS",
            self.camera_fps,
        )

        self.camera_section.add_row(
            "Backend",
            self.camera_backend,
        )

        self.gamepad_section = SetupSection("GAMEPAD")

        self.joystick_index = QSpinBox()
        self.joystick_index.setRange(
            0,
            15,
        )

        self.pan_axis_index = QComboBox()
        self.pan_axis_index.addItem(
            "Axis 0 — Left Stick X",
            0,
        )
        self.pan_axis_index.addItem(
            "Axis 1 — Left Stick Y",
            1,
        )
        self.pan_axis_index.addItem(
            "Axis 2",
            2,
        )
        self.pan_axis_index.addItem(
            "Axis 3",
            3,
        )

        self.tilt_axis_index = QComboBox()
        self.tilt_axis_index.addItem(
            "Axis 0 — Left Stick X",
            0,
        )
        self.tilt_axis_index.addItem(
            "Axis 1 — Left Stick Y",
            1,
        )
        self.tilt_axis_index.addItem(
            "Axis 2",
            2,
        )
        self.tilt_axis_index.addItem(
            "Axis 3",
            3,
        )

        self.mode_button_index = QComboBox()

        self.mode_button_index.addItem(
            "Button 4",
            4,
        )

        self.mode_button_index.addItem(
            "Button 5 — RB",
            5,
        )

        self.mode_button_index.addItem(
            "Button 6",
            6,
        )

        self.mode_button_index.addItem(
            "Button 7",
            7,
        )

        self.gamepad_dead_zone = QDoubleSpinBox()

        self.gamepad_dead_zone.setRange(
            0.0,
            1.0,
        )

        self.gamepad_dead_zone.setSingleStep(0.01)

        self.gamepad_dead_zone.setDecimals(2)

        self.invert_tilt = QCheckBox("Invert vertical direction")

        self.gamepad_section.add_row(
            "Controller Slot",
            self.joystick_index,
        )

        self.gamepad_section.add_row(
            "Pan Control",
            self.pan_axis_index,
        )

        self.gamepad_section.add_row(
            "Tilt Control",
            self.tilt_axis_index,
        )

        self.gamepad_section.add_row(
            "Mode Switch",
            self.mode_button_index,
        )

        self.gamepad_section.add_row(
            "Dead Zone",
            self.gamepad_dead_zone,
        )

        self.gamepad_section.add_row(
            "Tilt Direction",
            self.invert_tilt,
        )
        # =====================================================
        # OUTPUT
        # =====================================================
        self.output_section = SetupSection("OUTPUT")

        self.output_mode = QComboBox()

        self.output_mode.addItems(
            [
                "null",
                "serial",
            ]
        )

        self.output_section.add_row(
            "Output Mode",
            self.output_mode,
        )

        # =====================================================
        # SERIAL
        # =====================================================
        self.serial_section = SetupSection("SERIAL")

        self.serial_port = QLineEdit()

        self.serial_baudrate = QComboBox()
        self.serial_baudrate.addItems(
            [
                "9600",
                "57600",
                "115200",
                "230400",
                "460800",
            ]
        )

        self.write_timeout = QDoubleSpinBox()

        self.write_timeout.setRange(
            0.01,
            5.0,
        )

        self.write_timeout.setSingleStep(0.01)

        self.write_timeout.setDecimals(2)

        self.write_timeout.setSuffix(" s")

        self.serial_section.add_row(
            "Port",
            self.serial_port,
        )

        self.serial_section.add_row(
            "Baudrate",
            self.serial_baudrate,
        )

        self.serial_section.add_row(
            "Write Timeout",
            self.write_timeout,
        )

        # =====================================================
        # 2 x 2 DASHBOARD
        # =====================================================
        dashboard.addWidget(
            self.camera_section,
            0,
            0,
        )

        dashboard.addWidget(
            self.gamepad_section,
            0,
            1,
        )

        dashboard.addWidget(
            self.output_section,
            1,
            0,
        )

        dashboard.addWidget(
            self.serial_section,
            1,
            1,
        )

        dashboard.setColumnStretch(
            0,
            1,
        )

        dashboard.setColumnStretch(
            1,
            1,
        )

        dashboard.setRowStretch(
            0,
            3,
        )

        dashboard.setRowStretch(
            1,
            2,
        )

        root.addLayout(
            dashboard,
            1,
        )

        # =====================================================
        # BOTTOM ACTION BAR
        # =====================================================
        self.restart_notice = QLabel(
            "Thay đổi cấu hình sẽ có hiệu lực sau khi khởi động lại ứng dụng."
        )

        self.restart_notice.setProperty(
            "setupNotice",
            True,
        )

        self.reset_button = QPushButton("RESET")

        self.reset_button.setProperty(
            "secondaryButton",
            True,
        )

        self.save_button = QPushButton("SAVE CONFIG")

        self.save_button.setProperty(
            "primaryButton",
            True,
        )

        self.reset_button.clicked.connect(self._load_config)

        self.save_button.clicked.connect(self._save_config)

        bottom = QHBoxLayout()

        bottom.setSpacing(10)

        bottom.addWidget(self.restart_notice)

        bottom.addStretch()

        bottom.addWidget(self.reset_button)

        bottom.addWidget(self.save_button)

        root.addLayout(bottom)

        self._load_config()
        self.output_mode.currentTextChanged.connect(self._on_output_mode_changed)

    def _load_config(
        self,
    ) -> None:
        try:
            config = load_config(self._config_path)
        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            yaml.YAMLError,
        ) as exc:
            self.restart_notice.setText(f"RESET FAILED: {exc}")
            return

        self._config = config

        camera = config.camera
        gamepad = config.control.gamepad
        output = config.output

        self.camera_source.setText(str(camera.source))

        self.camera_width.setValue(camera.width)

        self.camera_height.setValue(camera.height)

        self.camera_fps.setValue(camera.fps)

        self.camera_backend.setCurrentText(camera.backend)

        self.joystick_index.setValue(gamepad.joystick_index)

        self.pan_axis_index.setCurrentIndex(
            max(
                0,
                self.pan_axis_index.findData(gamepad.pan_axis_index),
            )
        )

        self.tilt_axis_index.setCurrentIndex(
            max(
                0,
                self.tilt_axis_index.findData(gamepad.tilt_axis_index),
            )
        )

        self.mode_button_index.setCurrentIndex(
            max(
                0,
                self.mode_button_index.findData(gamepad.mode_button_index),
            )
        )

        self.gamepad_dead_zone.setValue(gamepad.dead_zone)

        self.invert_tilt.setChecked(gamepad.invert_tilt)

        self.output_mode.setCurrentText(output.mode)

        self.serial_port.setText(output.serial.port)

        self.serial_baudrate.setCurrentText(str(output.serial.baudrate))

        self.write_timeout.setValue(output.serial.write_timeout_s)
        self._on_output_mode_changed(self.output_mode.currentText())

        self.restart_notice.setText("Configuration loaded from disk.")

    def _save_config(self) -> None:
        valid, error_message = self._validate_inputs()

        if not valid:
            self.restart_notice.setText(f"SAVE FAILED: {error_message}")
            return

        config_path = self._config_path

        with config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            raw = yaml.safe_load(file)

        # ==========================================
        # CAMERA
        # ==========================================
        source_text = self.camera_source.text().strip()

        camera_source: int | str

        if source_text.isdigit():
            camera_source = int(source_text)
        else:
            camera_source = source_text

        raw["camera"]["source"] = camera_source

        raw["camera"]["width"] = self.camera_width.value()

        raw["camera"]["height"] = self.camera_height.value()

        raw["camera"]["fps"] = self.camera_fps.value()

        raw["camera"]["backend"] = self.camera_backend.currentText().lower()

        # ==========================================
        # GAMEPAD
        # ==========================================
        gamepad = raw["control"]["gamepad"]

        gamepad["joystick_index"] = self.joystick_index.value()

        gamepad["pan_axis_index"] = int(self.pan_axis_index.currentData())

        gamepad["tilt_axis_index"] = int(self.tilt_axis_index.currentData())

        gamepad["mode_button_index"] = int(self.mode_button_index.currentData())

        gamepad["dead_zone"] = self.gamepad_dead_zone.value()

        gamepad["invert_tilt"] = self.invert_tilt.isChecked()

        # ==========================================
        # OUTPUT
        # ==========================================
        raw["output"]["mode"] = self.output_mode.currentText().lower()

        serial = raw["output"]["serial"]

        serial["port"] = self.serial_port.text().strip()

        serial["baudrate"] = int(self.serial_baudrate.currentText())

        serial["write_timeout_s"] = self.write_timeout.value()

        # ==========================================
        # WRITE TEMP FILE FIRST
        # ==========================================
        temp_path = config_path.with_suffix(".yaml.tmp")

        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                yaml.safe_dump(
                    raw,
                    file,
                    sort_keys=False,
                    allow_unicode=True,
                )

            # Validate bằng đúng loader
            # mà runtime đang sử dụng.
            validated_config = load_config(temp_path)

            # Chỉ replace file thật
            # nếu validation thành công.
            temp_path.replace(config_path)

            self._config = validated_config

        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            yaml.YAMLError,
        ) as exc:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

            self.restart_notice.setText(f"SAVE FAILED: {exc}")

            return

        self.restart_notice.setText(
            "Configuration saved. Restart application to apply changes."
        )

    def _on_output_mode_changed(
        self,
        mode: str,
    ) -> None:
        serial_enabled = mode.strip().lower() == "serial"

        self.serial_section.setEnabled(serial_enabled)

    def _validate_inputs(
        self,
    ) -> tuple[bool, str]:
        camera_source = self.camera_source.text().strip()

        if not camera_source:
            return (
                False,
                "Camera source cannot be empty.",
            )

        if self.pan_axis_index.currentData() is None:
            return (
                False,
                "Invalid pan axis mapping.",
            )

        if self.tilt_axis_index.currentData() is None:
            return (
                False,
                "Invalid tilt axis mapping.",
            )

        if self.mode_button_index.currentData() is None:
            return (
                False,
                "Invalid mode button mapping.",
            )

        output_mode = self.output_mode.currentText().strip().lower()

        if output_mode not in {
            "null",
            "serial",
        }:
            return (
                False,
                "Invalid output mode.",
            )

        if output_mode == "serial":
            port = self.serial_port.text().strip()

            if not port:
                return (
                    False,
                    "Serial port cannot be empty.",
                )

            if not self.serial_baudrate.currentText().isdigit():
                return (
                    False,
                    "Invalid serial baudrate.",
                )

            if self.write_timeout.value() <= 0.0:
                return (
                    False,
                    "Write timeout must be greater than 0.",
                )

        return (
            True,
            "",
        )
