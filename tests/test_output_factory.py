from app.config import (
    OutputConfig,
    SerialOutputConfig,
)
from app.output.factory import build_command_output
from app.output.null import NullCommandOutput
from app.output.serial import SerialCommandOutput


def make_output_config(
    mode: str,
    port: str = "loop://",
) -> OutputConfig:
    return OutputConfig(
        mode=mode,
        serial=SerialOutputConfig(
            port=port,
            baudrate=115200,
            write_timeout_s=0.10,
        ),
    )


def test_builds_null_output() -> None:
    output = build_command_output(make_output_config("null"))

    assert isinstance(output, NullCommandOutput)

    output.close()


def test_builds_serial_output() -> None:
    output = build_command_output(make_output_config("serial"))

    try:
        assert isinstance(
            output,
            SerialCommandOutput,
        )
    finally:
        output.close()


def test_serial_requires_port() -> None:
    config = make_output_config(
        "serial",
        port="",
    )

    try:
        build_command_output(config)
    except ValueError as exc:
        assert "port" in str(exc)
    else:
        raise AssertionError("expected ValueError")
