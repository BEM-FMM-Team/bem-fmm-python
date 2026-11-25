from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEvent, QPoint

from bemfmm.gui.viewport import VIEW_PRESETS, Viewport


@pytest.mark.parametrize(
    ("angle_delta", "pixel_delta", "factor"),
    [(120, 0, 1.1), (-120, 0, 1 / 1.1), (0, 60, 1.1**0.5)],
)
def test_wheel_zoom_uses_qt_scroll_delta(angle_delta, pixel_delta, factor):
    camera = Mock()
    renderer = Mock()
    viewport = Viewport.__new__(Viewport)
    viewport.plt = SimpleNamespace(camera=camera, renderer=renderer)
    viewport.render = Mock()
    event = SimpleNamespace(
        type=lambda: QEvent.Wheel,
        angleDelta=lambda: QPoint(0, angle_delta),
        pixelDelta=lambda: QPoint(0, pixel_delta),
    )

    assert viewport._on_mouse(event)

    camera.Dolly.assert_called_once_with(factor)
    renderer.ResetCameraClippingRange.assert_called_once_with()
    viewport.render.assert_called_once_with()


@pytest.mark.parametrize(
    ("name", "position", "up"),
    [(name, *orientation) for name, orientation in VIEW_PRESETS.items()],
)
def test_view_preset_sets_camera_orientation(name, position, up):
    camera = Mock()
    renderer = Mock()
    viewport = Viewport.__new__(Viewport)
    viewport.plt = SimpleNamespace(camera=camera, renderer=renderer)
    viewport.render = Mock()

    viewport.view(name)

    camera.SetFocalPoint.assert_called_once_with(0, 0, 0)
    camera.SetPosition.assert_called_once_with(*position)
    camera.SetViewUp.assert_called_once_with(*up)
    renderer.ResetCamera.assert_called_once_with()
    viewport.render.assert_called_once_with()
