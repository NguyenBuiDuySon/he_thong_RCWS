from app.control.button import RisingEdgeButton


def test_rising_edge_fires_once() -> None:
    button = RisingEdgeButton()

    assert not button.update(False)

    assert button.update(True)

    assert not button.update(True)
    assert not button.update(True)

    assert not button.update(False)


def test_second_press_fires_again() -> None:
    button = RisingEdgeButton()

    assert button.update(True)
    assert not button.update(True)

    assert not button.update(False)

    assert button.update(True)


def test_reset_allows_new_press() -> None:
    button = RisingEdgeButton()

    assert button.update(True)

    button.reset()

    assert button.update(True)
