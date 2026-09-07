from exohspec_thar.fits import PUBLIC_HEADER_ALLOWLIST


def test_public_header_allowlist_is_minimal() -> None:
    assert PUBLIC_HEADER_ALLOWLIST == {"EXPTIME", "EXPOSURE"}
    forbidden = {"OBSERVER", "INSTRUME", "TELESCOP", "LATITUDE", "LONGITUD", "OBJECT"}
    assert PUBLIC_HEADER_ALLOWLIST.isdisjoint(forbidden)

