from __future__ import annotations

import numpy as np

from exohspec_thar.analysis import _asinh_display, _role


def test_exposure_roles_are_explicit() -> None:
    exposures = [30.0, 60.0, 120.0, 180.0]
    assert _role(30.0, exposures) == "protects bright line cores"
    assert _role(120.0, exposures) == "best single-frame balance"
    assert _role(180.0, exposures) == "reveals faint structure"


def test_display_transform_is_finite_and_monotonic() -> None:
    image = np.arange(100, dtype=float).reshape(10, 10)
    transformed = _asinh_display(image)
    assert np.isfinite(transformed).all()
    assert np.all(np.diff(transformed.ravel()) >= 0)

