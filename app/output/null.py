from app.control.types import PanTiltCommand


class NullCommandOutput:
    """Command sink used when no physical actuator is connected."""

    def __init__(self) -> None:
        self._closed = False

    def send(self, command: PanTiltCommand) -> None:
        if self._closed:
            raise RuntimeError("command output is closed")

        # Intentionally discard the command.
        _ = command

    def close(self) -> None:
        self._closed = True
