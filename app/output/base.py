from typing import Protocol

from app.control.types import PanTiltCommand


class CommandOutput(Protocol):
    def send(self, command: PanTiltCommand) -> None:
        """Send the latest final pan/tilt command."""
        ...

    def close(self) -> None:
        """Release output resources."""
        ...
