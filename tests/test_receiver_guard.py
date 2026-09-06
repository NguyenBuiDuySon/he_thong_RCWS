from app.output.protocol import WireCommand
from app.output.receiver_guard import ReceiverCommandGuard


def make_command(
    sequence: int,
    *,
    active: bool = True,
) -> WireCommand:
    return WireCommand(
        sequence=sequence,
        active=active,
        pan_milli=250 if active else 0,
        tilt_milli=-100 if active else 0,
    )


def test_accepts_first_valid_command() -> None:
    guard = ReceiverCommandGuard(timeout_s=0.25)

    assert guard.should_stop(now_ns=0)

    assert guard.accept(
        make_command(10),
        now_ns=0,
    )

    assert not guard.should_stop(now_ns=100_000_000)


def test_replay_does_not_refresh_timeout() -> None:
    guard = ReceiverCommandGuard(timeout_s=0.25)

    assert guard.accept(
        make_command(10),
        now_ns=0,
    )

    assert not guard.accept(
        make_command(10),
        now_ns=200_000_000,
    )

    assert guard.should_stop(
        now_ns=250_000_000,
    )


def test_timeout_allows_new_sender_session() -> None:
    guard = ReceiverCommandGuard(timeout_s=0.25)

    assert guard.accept(
        make_command(5000),
        now_ns=0,
    )

    assert guard.should_stop(
        now_ns=300_000_000,
    )

    assert guard.accept(
        make_command(0),
        now_ns=300_000_000,
    )

    assert not guard.should_stop(
        now_ns=300_000_000,
    )


def test_inactive_command_requests_stop() -> None:
    guard = ReceiverCommandGuard(timeout_s=0.25)

    assert guard.accept(
        make_command(20),
        now_ns=0,
    )

    assert guard.accept(
        make_command(
            21,
            active=False,
        ),
        now_ns=10_000_000,
    )

    assert guard.should_stop(
        now_ns=10_000_000,
    )
