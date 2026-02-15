"""
PII detection and stripping utilities.

Used when ingesting documents (CVs, publication lists, etc.) to extract
research content while discarding personally identifiable information.

Privacy principles:
- Strip names, emails, phone numbers, addresses, institutional affiliations
- Keep research topics, methodologies, domains, techniques
- When in doubt, strip it — false positives are acceptable, PII leaks are not
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Optional


# Patterns for common PII
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}")
_URL_RE = re.compile(r"https?://\S+")
_ORCID_RE = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")

# Address-like patterns (street numbers, zip codes, etc.)
_ADDRESS_RE = re.compile(
    r"\b\d{1,5}\s+[A-Z][a-z]+\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane)\b",
    re.IGNORECASE,
)
_ZIPCODE_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")

# Lines that likely contain PII headers
_PII_HEADER_KEYWORDS = {
    "address", "phone", "telephone", "mobile", "fax", "email", "e-mail",
    "contact", "home", "residence", "nationality", "date of birth", "dob",
    "passport", "social security", "ssn", "driver", "license",
    "marital status", "gender", "age", "born",
}


@dataclass
class StrippedDocument:
    """Result of PII stripping: clean text + metadata about what was removed."""
    clean_text: str
    pii_removed_count: int = 0
    source_hash: str = ""
    warnings: List[str] = field(default_factory=list)


def compute_document_hash(content: str) -> str:
    """SHA-256 hash of document content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def strip_pii(text: str) -> StrippedDocument:
    """Remove PII from text, keeping research-relevant content.

    Returns a StrippedDocument with the cleaned text and removal stats.
    """
    source_hash = compute_document_hash(text)
    pii_count = 0
    warnings = []

    # Replace emails
    emails_found = _EMAIL_RE.findall(text)
    if emails_found:
        text = _EMAIL_RE.sub("[EMAIL_REMOVED]", text)
        pii_count += len(emails_found)

    # Replace phone numbers
    phones_found = _PHONE_RE.findall(text)
    if phones_found:
        text = _PHONE_RE.sub("[PHONE_REMOVED]", text)
        pii_count += len(phones_found)

    # Replace URLs (these could contain identifying info like personal pages)
    urls_found = _URL_RE.findall(text)
    if urls_found:
        text = _URL_RE.sub("[URL_REMOVED]", text)
        pii_count += len(urls_found)

    # Replace ORCID identifiers
    orcids_found = _ORCID_RE.findall(text)
    if orcids_found:
        text = _ORCID_RE.sub("[ORCID_REMOVED]", text)
        pii_count += len(orcids_found)

    # Replace addresses
    addresses_found = _ADDRESS_RE.findall(text)
    if addresses_found:
        text = _ADDRESS_RE.sub("[ADDRESS_REMOVED]", text)
        pii_count += len(addresses_found)

    # Remove lines that look like PII headers
    clean_lines = []
    for line in text.split("\n"):
        line_lower = line.strip().lower()
        # Skip lines that are primarily PII labels
        if any(kw in line_lower for kw in _PII_HEADER_KEYWORDS) and len(line.strip()) < 100:
            pii_count += 1
            continue
        # Skip lines that are just removal markers
        if line.strip() in ("[EMAIL_REMOVED]", "[PHONE_REMOVED]", "[URL_REMOVED]",
                           "[ORCID_REMOVED]", "[ADDRESS_REMOVED]"):
            continue
        clean_lines.append(line)

    clean_text = "\n".join(clean_lines)

    # Clean up excessive whitespace left by removals
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
    clean_text = re.sub(r"\[(?:EMAIL|PHONE|URL|ORCID|ADDRESS)_REMOVED\]", "", clean_text)
    clean_text = clean_text.strip()

    if pii_count > 0:
        warnings.append(f"Stripped {pii_count} PII item(s) from document")

    return StrippedDocument(
        clean_text=clean_text,
        pii_removed_count=pii_count,
        source_hash=source_hash,
        warnings=warnings,
    )


def validate_no_pii(text: str) -> List[str]:
    """Check user-submitted text for accidental PII.

    Returns a list of warnings if PII patterns are detected.
    Used to warn users when they're about to save PII in free-text fields.
    """
    warnings = []

    if _EMAIL_RE.search(text):
        warnings.append("Text appears to contain an email address. "
                        "For your privacy, avoid including contact details.")
    if _PHONE_RE.search(text):
        warnings.append("Text appears to contain a phone number. "
                        "For your privacy, avoid including contact details.")
    if _ORCID_RE.search(text):
        warnings.append("Text appears to contain an ORCID identifier. "
                        "This can be used to identify you directly.")
    if _ADDRESS_RE.search(text):
        warnings.append("Text appears to contain a physical address.")

    return warnings
