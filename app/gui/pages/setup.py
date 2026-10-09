from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig


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

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(
            18,
            16,
            18,
            16,
        )
        self.grid.setHorizontalSpacing(18)
        self.grid.setVerticalSpacing(12)

        title_label = QLabel(title)
        title_label.setProperty(
            "setupSectionTitle",
            True,
        )

        self.grid.addWidget(
            title_label,
            0,
            0,
            1,
            2,
        )

        self._row = 1

    def add_row(
        self,
        label: str,
        widget: QWidget,
    ) -> None:
        label_widget = QLabel(label)
        label_widget.setProperty(
            "setupLabel",
            True,
        )

        self.grid.addWidget(
            label_widget,
            self._row,
            0,
        )

        self.grid.addWidget(
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

        root = QVBoxLayout(self)
        root.setContentsMargins(
            28,
            24,
            28,
            24,
        )
        root.setSpacing(18)

        title = QLabel("SETUP")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Cấu hình camera, gamepad và output hệ thống")
        subtitle.setObjectName("pageSubtitle")

        root.addWidget(title)
        root.addWidget(subtitle)

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

        self.pan_axis_index = QSpinBox()
        self.pan_axis_index.setRange(
            0,
            15,
        )

        self.tilt_axis_index = QSpinBox()
        self.tilt_axis_index.setRange(
            0,
            15,
        )

        self.mode_button_index = QSpinBox()
        self.mode_button_index.setRange(
            0,
            31,
        )

        self.gamepad_dead_zone = QDoubleSpinBox()
        self.gamepad_dead_zone.setRange(
            0.0,
            1.0,
        )
        self.gamepad_dead_zone.setSingleStep(0.01)
        self.gamepad_dead_zone.setDecimals(2)

        self.invert_tilt = QCheckBox("Invert tilt axis")

        self.gamepad_section.add_row(
            "Joystick Index",
            self.joystick_index,
        )
        self.gamepad_section.add_row(
            "Pan Axis",
            self.pan_axis_index,
        )
        self.gamepad_section.add_row(
            "Tilt Axis",
            self.tilt_axis_index,
        )
        self.gamepad_section.add_row(
            "Mode Button",
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

        self.output_section = SetupSection("OUTPUT / SERIAL")

        self.output_mode = QComboBox()
        self.output_mode.addItems(
            [
                "null",
                "serial",
            ]
        )

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

        self.output_section.add_row(
            "Output Mode",
            self.output_mode,
        )
        self.output_section.add_row(
            "Serial Port",
            self.serial_port,
        )
        self.output_section.add_row(
            "Baudrate",
            self.serial_baudrate,
        )
        self.output_section.add_row(
            "Write Timeout",
            self.write_timeout,
        )

        root.addWidget(self.camera_section)
        root.addWidget(self.gamepad_section)
        root.addWidget(self.output_section)

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

        # G5B sẽ nối SAVE thật.
        self.save_button.setEnabled(False)

        root.addWidget(self.restart_notice)
        root.addWidget(self.reset_button)
        root.addWidget(self.save_button)

        root.addStretch()

        self._load_config()

    def _load_config(self) -> None:
        camera = self._config.camera
        gamepad = self._config.control.gamepad
        output = self._config.output

        self.camera_source.setText(str(camera.source))

        self.camera_width.setValue(camera.width)

        self.camera_height.setValue(camera.height)

        self.camera_fps.setValue(camera.fps)

        self.camera_backend.setCurrentText(camera.backend)

        self.joystick_index.setValue(gamepad.joystick_index)

        self.pan_axis_index.setValue(gamepad.pan_axis_index)

        self.tilt_axis_index.setValue(gamepad.tilt_axis_index)

        self.mode_button_index.setValue(gamepad.mode_button_index)

        self.gamepad_dead_zone.setValue(gamepad.dead_zone)

        self.invert_tilt.setChecked(gamepad.invert_tilt)

        self.output_mode.setCurrentText(output.mode)

        self.serial_port.setText(output.serial.port)

        self.serial_baudrate.setCurrentText(str(output.serial.baudrate))

        self.write_timeout.setValue(output.serial.write_timeout_s)
