from app.security.masker import SensitiveDataMasker


def test_mask_ssn_shows_last_four():
    """
    SSN masking should preserve only the last four digits.
    """
    masker = SensitiveDataMasker()
    assert masker.mask_ssn("123-45-6789") == "***-**-6789"


def test_mask_name_hides_remaining_characters():
    """
    Name masking should keep the first character and hide the rest.
    """
    masker = SensitiveDataMasker()
    assert masker.mask_name("Alice") == "A****"
