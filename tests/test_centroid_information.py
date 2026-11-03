import numpy as np
import pytest
from research.centroid_information import (
    gaussian_pixel_profile, centroid_crlb, exposure_ladder_information,
)

P = np.arange(-10., 11.)


def test_pixel_integration_conserves_area():
    for centre in (-0.4, 0.0, 0.3):
        assert np.sum(gaussian_pixel_profile(centre, 1.2, P, samples=256)) == pytest.approx(1, abs=1e-8)


def test_information_scales_with_exposure_in_shot_noise_limit():
    a = centroid_crlb(P, .2, 1.1, 500, 10)
    b = centroid_crlb(P, .2, 1.1, 500, 40)
    assert b / a == pytest.approx(0.5, rel=1e-6)


def test_independent_unsaturated_exposures_add_information():
    a = centroid_crlb(P, .1, 1.2, 100, 30, background_rate=2)
    b = exposure_ladder_information(P, .1, 1.2, 100, [30, 30], background_rate=2)
    assert b['sigma_px'] == pytest.approx(a / np.sqrt(2), rel=1e-6)


def test_saturation_mask_is_conservative():
    full = exposure_ladder_information(P, .1, 1.2, 800, [30, 180], ceiling=1e9)
    clipped = exposure_ladder_information(P, .1, 1.2, 800, [30, 180], ceiling=30000)
    assert clipped['sigma_px'] >= full['sigma_px']
    assert clipped['retained_pixels'] < full['retained_pixels']


def test_invalid_inputs():
    with pytest.raises(ValueError):
        gaussian_pixel_profile(0, -1, P)
    with pytest.raises(ValueError):
        exposure_ladder_information(P, 0, 1, 100, [0])
