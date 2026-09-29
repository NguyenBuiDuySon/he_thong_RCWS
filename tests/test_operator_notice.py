import pytest

from app.hud.notice import OperatorNotice


def test_notice_is_visible_before_expiry() -> None:
    notice = OperatorNotice(duration_s=1.0)

    notice.show(
        "TARGET SELECTED",
        now_ns=1_000_000_000,
    )

    assert notice.read(now_ns=1_500_000_000) == "TARGET SELECTED"


def test_notice_expires() -> None:
    notice = OperatorNotice(duration_s=1.0)

    notice.show(
        "TARGET SELECTED",
        now_ns=1_000_000_000,
    )

    assert notice.read(now_ns=2_000_000_000) is None


def test_new_notice_replaces_old_notice() -> None:
    notice = OperatorNotice()

    notice.show(
        "SELECT MISS",
        now_ns=1_000,
    )

    notice.show(
        "TARGET SELECTED",
        now_ns=2_000,
    )

    assert notice.read(now_ns=3_000) == "TARGET SELECTED"


def test_rejects_invalid_duration() -> None:
    with pytest.raises(
        ValueError,
        match="duration_s",
    ):
        OperatorNotice(duration_s=0.0)
