"""
Field Parser — OCR Text → Structured Transaction Dictionary.
Person 2 (Nivash) — UPI Transaction Fraud Forensics Platform (IDP).

Handles real OCR artifacts: Tesseract often misreads '₹' as '%', '*', or 't'.
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Amount
# ---------------------------------------------------------------------------

def parse_amount(text: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Extracts transaction amount. Handles ₹/%/*/t OCR misreads and
    comma-separated thousands (₹1,200.00).

    Returns: (formatted "₹450.00", float 450.0) or (None, None)
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    candidates: list = []

    # Strategy 1 — currency-prefixed (₹, %, *, t, Rs., INR)
    for line in lines:
        m = re.search(
            r'([₹%*tF]|Rs\.?|INR)\s*([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2}|[0-9]+\.[0-9]{2})',
            line, re.IGNORECASE
        )
        if m:
            try:
                val = float(m.group(2).replace(',', ''))
                if 0.5 <= val <= 1_000_000:
                    candidates.append((val, f"₹{val:,.2f}", 10))
            except ValueError:
                pass

    # Strategy 2 — standalone decimal line ("85.50", "1,200.00")
    for line in lines:
        m = re.fullmatch(r'([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2}|[0-9]+\.[0-9]{2})', line)
        if m:
            try:
                val = float(m.group(1).replace(',', ''))
                if 0.5 <= val <= 1_000_000:
                    candidates.append((val, f"₹{val:,.2f}", 5))
            except ValueError:
                pass

    if candidates:
        candidates.sort(key=lambda c: c[2], reverse=True)
        return candidates[0][1], candidates[0][0]
    return None, None


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

_DATE_TEXT = re.compile(
    r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
    re.IGNORECASE,
)
_DATE_ISO = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
_DATE_SLASH = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')


def parse_date(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Returns (display "12 Mar 2026", iso "2026-03-12") or (None, None)."""
    m = _DATE_TEXT.search(text)
    if m:
        for fmt in ("%d %b %Y", "%d %B %Y"):
            try:
                dt = datetime.strptime(m.group(1), fmt)
                return dt.strftime("%d %b %Y"), dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

    m = _DATE_ISO.search(text)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d")
            return dt.strftime("%d %b %Y"), dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    m = _DATE_SLASH.search(text)
    if m:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(m.group(1), fmt)
                return dt.strftime("%d %b %Y"), dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

    return None, None


# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------

# 12-hour with AM/PM (preferred, most common in receipts)
_TIME_12H = re.compile(
    r'\b((?:0?[1-9]|1[0-2]):[0-5][0-9](?::[0-5][0-9])?\s*(?:AM|PM|am|pm))\b'
)
# 24-hour without AM/PM (hour 13-23 unambiguous; 0-12 needs AM/PM context)
_TIME_24H = re.compile(
    r'\b((?:1[3-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?)\b'
)
# Combined fallback
_TIME = _TIME_12H


def parse_time(text: str) -> Optional[str]:
    """Extracts timestamp — prefers 12h AM/PM, falls back to 24h."""
    def _search(line: str):
        m = _TIME_12H.search(line)
        if m:
            return m.group(1).strip()
        m = _TIME_24H.search(line)
        if m:
            return m.group(1).strip()
        return None

    for line in text.splitlines():
        if "time" in line.lower():
            result = _search(line)
            if result:
                return result
    # General scan
    result = _search(text)
    return result


# ---------------------------------------------------------------------------
# UTR / Transaction ID
# ---------------------------------------------------------------------------

_UTR_CONTEXT = re.compile(
    r'(?:UPI\s*(?:Ref|Transaction\s*ID|Reference|Ref\s*\(UTR\))|UTR\s*Number|UTR|Transaction\s*ID)'
    r'[:\s\(\)]*([A-Za-z0-9]{6,20})',
    re.IGNORECASE,
)
_UTR_12DIGIT = re.compile(r'\b(\d{12})\b')
_UTR_ALPHA = re.compile(r'\b(UTR[A-Za-z0-9]{5,15})\b', re.IGNORECASE)


def parse_utr(text: str) -> Optional[str]:
    """Extracts 12-digit UTR or tampered alphanumeric transaction IDs."""
    m = _UTR_CONTEXT.search(text)
    if m:
        val = re.sub(r'[^A-Za-z0-9]', '', m.group(1))
        if len(val) >= 6:
            return val

    m = _UTR_ALPHA.search(text)
    if m:
        return m.group(1).strip()

    m = _UTR_12DIGIT.search(text)
    if m:
        return m.group(1).strip()

    return None


# ---------------------------------------------------------------------------
# Template / App Name
# ---------------------------------------------------------------------------

def parse_template_type(text: str) -> str:
    tl = text.lower()
    if "paylite" in tl:
        return "PayLite"
    if "quickpe" in tl or "uclpe" in tl or "ucipe" in tl or "quick pe" in tl:
        return "QuickPe"
    if "unipay" in tl or "uni pay" in tl:
        return "UniPay"
    # Legacy aliases
    if "apexpay" in tl:
        return "PayLite"
    if "zenithupi" in tl or "zenith" in tl:
        return "QuickPe"
    if "novapay" in tl:
        return "UniPay"
    return "GenericUPI"


# ---------------------------------------------------------------------------
# Recipient
# ---------------------------------------------------------------------------

_KNOWN_RECIPIENTS = [
    "Metro Book Store", "Sunrise Cafe", "Apex Mart", "Green Grocers",
    "Urban Coffee", "City Pharmacy", "Modern Bakery", "Quick Mart",
    "Tech Zone", "Campus Canteen", "Blue Star Electronics",
    "Green Grocers Mart", "Apex Stationery", "Urban Coffee Roasters",
    "City Pharmacy Retail", "Modern Bakery Store", "City Electronics",
]


def parse_recipient(text: str) -> Optional[str]:
    tl = text.lower()
    for rec in _KNOWN_RECIPIENTS:
        if rec.lower() in tl:
            return rec
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        for prefix in ("paid to", "paid to:", "to recipient", "transfer to", "recipient name", "recipient"):
            if prefix in line.lower():
                cleaned = re.sub(re.escape(prefix), '', line, flags=re.IGNORECASE).strip(": \t-—")
                if cleaned and len(cleaned) > 2:
                    return cleaned
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(k in next_line.lower() for k in ("amount", "paid from", "ref", "date", "status")):
                        return next_line
    return None


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def parse_transaction_status(text: str) -> str:
    tl = text.lower()
    if "paid successfully" in tl or "pald successfully" in tl:
        return "Paid Successfully"
    if "payment completed" in tl or "completed" in tl:
        return "Payment Completed"
    if "transaction successful" in tl:
        return "Transaction Successful"
    if "payment confirmed" in tl:
        return "Payment Confirmed"
    if "success" in tl:
        return "SUCCESS"
    return "Unknown"


# ---------------------------------------------------------------------------
# Master Parser
# ---------------------------------------------------------------------------

def parse_all_fields(raw_text: str) -> Dict[str, Any]:
    """
    Parses all transaction fields from raw Tesseract output.
    Primary function consumed by extractor.py.
    """
    amount_str, amount_val = parse_amount(raw_text)
    date_str, date_iso = parse_date(raw_text)
    return {
        "amount": amount_str,
        "amount_value": amount_val,
        "date": date_str,
        "date_iso": date_iso,
        "time": parse_time(raw_text),
        "transaction_id": parse_utr(raw_text),
        "template_type": parse_template_type(raw_text),
        "recipient": parse_recipient(raw_text),
        "status": parse_transaction_status(raw_text),
        "raw_text": raw_text,
    }


# Alias
parse_transaction_fields = parse_all_fields
