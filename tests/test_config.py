from app.config import load_config


def test_default_config_loads() -> None:
    config = load_config("configs/default.yaml")

    assert config.control.watchdog_timeout_s == 0.25
    assert config.control.kp_pan == 1.0
    assert config.control.kp_tilt == 1.0

    assert config.output.mode == "null"
    assert config.output.serial.baudrate == 115200
    assert config.output.serial.write_timeout_s == 0.10

    assert config.control.gamepad.joystick_index == 0
    assert config.control.gamepad.pan_axis_index == 0
    assert config.control.gamepad.tilt_axis_index == 1
    assert config.control.gamepad.mode_button_index == 5
    assert config.control.gamepad.dead_zone == 0.10
    assert config.control.gamepad.invert_tilt is True
