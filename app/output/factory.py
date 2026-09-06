from app.config import OutputConfig
from app.output.base import CommandOutput
from app.output.null import NullCommandOutput
from app.output.serial import SerialCommandOutput


def build_command_output(
    config: OutputConfig,
) -> CommandOutput:
    if config.mode == "null":
        return NullCommandOutput()

    if config.mode == "serial":
        if not config.serial.port:
            raise ValueError(
                "output.serial.port must not be empty when output.mode='serial'"
            )

        return SerialCommandOutput(
            config.serial.port,
            baudrate=config.serial.baudrate,
            write_timeout_s=config.serial.write_timeout_s,
        )

    raise ValueError(f"unsupported output mode: {config.mode!r}")
