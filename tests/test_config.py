from app.config import load_config


def test_default_config_loads() -> None:
    config = load_config("configs/default.yaml")

    assert config.control.watchdog_timeout_s == 0.25
    assert config.control.kp_pan == 1.0
    assert config.control.kp_tilt == 1.0

    assert config.output.mode == "null"
    assert config.output.serial.baudrate == 115200
    assert config.output.serial.write_timeout_s == 0.10
