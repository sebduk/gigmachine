"""Tests for PII detection and stripping."""
from backend.utils.privacy import strip_pii, validate_no_pii


def test_strip_email():
    result = strip_pii("Contact me at john.doe@university.edu for details.")
    assert "john.doe@university.edu" not in result.clean_text
    assert result.pii_removed_count >= 1


def test_strip_phone():
    result = strip_pii("Call me at +1 (555) 123-4567 about the grant.")
    assert "555" not in result.clean_text
    assert result.pii_removed_count >= 1


def test_strip_orcid():
    result = strip_pii("My ORCID is 0000-0002-1825-0097.")
    assert "0000-0002-1825-0097" not in result.clean_text
    assert result.pii_removed_count >= 1


def test_strip_url():
    result = strip_pii("See my profile at https://university.edu/~jdoe/publications")
    assert "https://university.edu" not in result.clean_text


def test_keeps_research_content():
    text = (
        "My research focuses on machine learning applications in genomics. "
        "I use deep neural networks and transformer architectures to analyze "
        "gene expression patterns in cancer cells."
    )
    result = strip_pii(text)
    assert "machine learning" in result.clean_text
    assert "genomics" in result.clean_text
    assert "transformer architectures" in result.clean_text
    assert result.pii_removed_count == 0


def test_strips_contact_header_lines():
    text = "John Doe\nEmail: john@example.com\nPhone: 555-1234\n\nResearch on quantum computing"
    result = strip_pii(text)
    assert "quantum computing" in result.clean_text
    assert "john@example.com" not in result.clean_text


def test_source_hash_consistent():
    text = "Research on climate modeling"
    r1 = strip_pii(text)
    r2 = strip_pii(text)
    assert r1.source_hash == r2.source_hash
    assert len(r1.source_hash) == 64  # SHA-256


def test_validate_no_pii_clean():
    warnings = validate_no_pii("I study machine learning applied to materials science.")
    assert len(warnings) == 0


def test_validate_no_pii_detects_email():
    warnings = validate_no_pii("I'm available at researcher@uni.edu for collaboration.")
    assert any("email" in w.lower() for w in warnings)


def test_validate_no_pii_detects_orcid():
    warnings = validate_no_pii("My ORCID: 0000-0002-1825-0097")
    assert any("orcid" in w.lower() for w in warnings)
