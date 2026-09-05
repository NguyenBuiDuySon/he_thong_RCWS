from types import SimpleNamespace
from typing import Any

import pytest

from app.control.watchdog import CommandWatchdog


class SpyOutput:
    def __init__(self) -> None:
        self.sent: list[Any] = []
        self.stop_calls = 0
        self.close_calls = 0

    def send(self, command: Any) -> None:
        self.sent.append(command)

    def stop(self) -> None:
        self.stop_calls += 1

    def close(self) -> None:
        self.close_calls += 1


def make_command(*, active: bool = True) -> Any:
    return SimpleNamespace(active=active)


def test_forwards_active_command() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    command = make_command(active=True)

    watchdog.send(command, now_ns=1_000_000_000)

    assert output.sent == [command]
    assert output.stop_calls == 0


def test_does_not_timeout_before_deadline() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.send(
        make_command(active=True),
        now_ns=1_000_000_000,
    )

    watchdog.update(now_ns=1_249_999_999)

    assert output.stop_calls == 0


def test_stops_at_timeout() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.send(
        make_command(active=True),
        now_ns=1_000_000_000,
    )

    watchdog.update(now_ns=1_250_000_000)

    assert output.stop_calls == 1


def test_inactive_command_stops_active_output() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.send(
        make_command(active=True),
        now_ns=1_000_000_000,
    )

    watchdog.send(
        make_command(active=False),
        now_ns=1_100_000_000,
    )

    assert output.stop_calls == 1


def test_timeout_stop_is_not_repeated() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.send(
        make_command(active=True),
        now_ns=1_000_000_000,
    )

    watchdog.update(now_ns=1_250_000_000)
    watchdog.update(now_ns=1_500_000_000)

    assert output.stop_calls == 1


def test_close_stops_before_closing() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.send(
        make_command(active=True),
        now_ns=1_000_000_000,
    )

    watchdog.close()

    assert output.stop_calls == 1
    assert output.close_calls == 1


def test_close_is_idempotent() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.close()
    watchdog.close()

    assert output.close_calls == 1


def test_rejects_send_after_close() -> None:
    output = SpyOutput()
    watchdog = CommandWatchdog(output, timeout_s=0.25)

    watchdog.close()

    with pytest.raises(RuntimeError, match="closed"):
        watchdog.send(make_command(active=True))


def test_rejects_invalid_timeout() -> None:
    output = SpyOutput()

    with pytest.raises(ValueError, match="timeout_s"):
        CommandWatchdog(output, timeout_s=0.0)
