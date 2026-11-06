"""Detector-domain centroid information and exposure-ladder sensitivity.

All quantities are synthetic ADU-equivalent electron counts; no wavelength
solution, calibrated detector gain, or EXOhSPEC RV precision is inferred.
"""
import numpy as np


def gaussian_pixel_profile(centroid_px, sigma_px, pixels, samples=64):
    """Pixel-integrated unit-area Gaussian, using midpoint quadrature."""
    p = np.asarray(pixels, dtype=float)
    if p.ndim != 1 or p.size < 3 or not np.all(np.isfinite(p)):
        raise ValueError('pixels must be a finite one-dimensional array')
    if not np.isfinite(sigma_px) or sigma_px <= 0 or samples < 2:
        raise ValueError('invalid Gaussian width or quadrature samples')
    offsets = (np.arange(samples) + 0.5) / samples - 0.5
    z = (p[:, None] + offsets[None, :] - centroid_px) / sigma_px
    return np.exp(-0.5 * z*z).mean(axis=1) / (np.sqrt(2*np.pi) * sigma_px)


def centroid_crlb(pixels, centroid_px, sigma_px, total_rate, exposure_seconds,
                  background_rate=0., read_noise=0., step=1e-3):
    """Conditional Gaussian-variance Fisher bound for centroid position.

    Fixed variance approximation: variance=source+background+read_noise^2.
    Derivative of variance with centroid is intentionally not included.
    """
    if any(not np.isfinite(v) or v < 0 for v in
           (total_rate, exposure_seconds, background_rate, read_noise)):
        raise ValueError('rates, exposure and read noise must be nonnegative finite')
    if total_rate == 0 or exposure_seconds == 0 or step <= 0:
        raise ValueError('nonzero source, exposure and derivative step required')
    profile = gaussian_pixel_profile(centroid_px, sigma_px, pixels)
    plus = gaussian_pixel_profile(centroid_px + step, sigma_px, pixels)
    minus = gaussian_pixel_profile(centroid_px - step, sigma_px, pixels)
    signal = total_rate * exposure_seconds * profile
    derivative = total_rate * exposure_seconds * (plus-minus) / (2*step)
    variance = signal + background_rate * exposure_seconds + read_noise**2
    if np.any(variance <= 0):
        raise ValueError('positive pixel variance required')
    fisher = np.sum(derivative**2 / variance)
    if fisher <= 0 or not np.isfinite(fisher):
        raise ValueError('zero centroid information')
    return float(1/np.sqrt(fisher))


def exposure_ladder_information(pixels, centroid_px, sigma_px, total_rate,
                                exposures, background_rate=0., read_noise=0.,
                                ceiling=60000., step=1e-3):
    """Sum independent-exposure Fisher information, masking saturated pixels.

    Assumes exposures are independent and source profile stable across frames.
    """
    t = np.asarray(exposures, dtype=float)
    if t.ndim != 1 or t.size == 0 or not np.all(np.isfinite(t)) or np.any(t <= 0):
        raise ValueError('exposures must be a positive finite vector')
    if ceiling <= 0 or not np.isfinite(ceiling):
        raise ValueError('ceiling must be positive')
    profile = gaussian_pixel_profile(centroid_px, sigma_px, pixels)
    plus = gaussian_pixel_profile(centroid_px + step, sigma_px, pixels)
    minus = gaussian_pixel_profile(centroid_px - step, sigma_px, pixels)
    information = 0.
    retained = 0
    for duration in t:
        signal = total_rate * duration * profile
        expected = signal + background_rate * duration
        good = expected < ceiling
        variance = expected + read_noise**2
        good &= variance > 0
        derivative = total_rate * duration * (plus-minus) / (2*step)
        information += float(np.sum(derivative[good]**2 / variance[good]))
        retained += int(np.sum(good))
    if information <= 0:
        raise ValueError('all informative pixels saturated or invalid')
    return {'sigma_px': float(1/np.sqrt(information)), 'retained_pixels': retained}
