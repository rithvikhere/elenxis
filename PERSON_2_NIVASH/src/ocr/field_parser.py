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
    Extracts transaction amount from OCR text.
    Handles currency symbols (₹, %, *, t, F, =, ~, §, Rs., INR),
    PhonePe Debited/Credited lines, Google Pay centred amounts,
    and trailing amounts on payee lines.

    Returns: (formatted "₹450.00", float 450.0) or (None, None)
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    candidates: list = []

    def _looks_like_date_line(line: str) -> bool:
        if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b', line, re.IGNORECASE):
            return True
        if re.search(r'\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b', line):
            return True
        return False

    # Strategy 0 (High Priority) — PhonePe Debited from / Credited to lines
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ("debited from", "credited to")):
            for next_l in lines[i + 1: i + 3]:
                m = re.search(
                    r'(?:XXXXXX\d{4}|X+\d{4})[^\d]*((?<![A-Za-z])[Ft]|[₹%*~=§27])?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)',
                    next_l, re.IGNORECASE
                )
                if m:
                    num_str = m.group(2).replace(',', '')
                    if num_str == "101010":
                        continue
                    try:
                        val = float(num_str)
                        if val > 20000 and num_str.startswith('2') and len(num_str) > 4:
                            val = float(num_str[1:])
                        if 0.5 <= val <= 1_000_000:
                            candidates.append((val, f"₹{val:,.2f}", 15))
                    except ValueError:
                        pass

    # Strategy 1 — currency-prefixed (₹, %, *, t, F, =, ~, §, Rs., INR)
    for line in lines:
        if _looks_like_date_line(line):
            continue
        m = re.search(
            r'((?<![A-Za-z])[Ft]|[₹%*~=§]|(?<![A-Za-z])Rs\.?|(?<![A-Za-z])INR)\s*(?<!\d)([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)(?!\d)',
            line, re.IGNORECASE
        )
        if m:
            num_str = m.group(2).replace(',', '')
            try:
                val = float(num_str)
                if 0.5 <= val <= 1_000_000:
                    weight = 12 if '.' in num_str else 10
                    candidates.append((val, f"₹{val:,.2f}", weight))
            except ValueError:
                pass

    # Strategy 1.5 — Payee / Banner trailing amount (e.g. CONTRACTORS 73,000 -> 3,000, REDBUS 21,750.39 -> 1,750.39)
    for line in lines:
        if _looks_like_date_line(line) or "bank" in line.lower() or "utr" in line.lower() or "id" in line.lower():
            continue
        m = re.search(
            r'[\s@#*~|<]+([₹%*~=§27])?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)$',
            line
        )
        if m and m.group(1):
            num_str = m.group(2).replace(',', '')
            try:
                val = float(num_str)
                if val > 20000 and num_str.startswith('2') and len(num_str) > 4:
                    val = float(num_str[1:])
                if 0.5 <= val <= 1_000_000:
                    candidates.append((val, f"₹{val:,.2f}", 12))
            except ValueError:
                pass

    # Strategy 2 — contextual prefix (Amount, Paid, Payment of, Received from, Total)
    for line in lines:
        if _looks_like_date_line(line):
            continue
        m = re.search(
            r'(?:Amount|Paid|Payment(?:\s*of)?|Received(?:\s*from)?|Total)\s*[:\-]?\s*((?<![A-Za-z])[Ft]|[₹%*~=§27]|Rs\.?|INR)?\s*(?<!\d)([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)(?!\d)',
            line, re.IGNORECASE
        )
        if m:
            num_str = m.group(2).replace(',', '')
            try:
                val = float(num_str)
                if val > 20000 and num_str.startswith('2') and len(num_str) > 4:
                    val = float(num_str[1:])
                if 0.5 <= val <= 1_000_000:
                    weight = 11 if '.' in num_str else 9
                    candidates.append((val, f"₹{val:,.2f}", weight))
            except ValueError:
                pass

    # Strategy 3 — Google Pay Large Centred Amount (between To and Completed)
    for i, line in enumerate(lines):
        if line.lower().startswith("to ") or line.lower() == "to":
            for next_l in lines[i + 1: i + 4]:
                if any(k in next_l.lower() for k in ("completed", "upi", "from", "+91", "date")):
                    continue
                m = re.match(
                    r'^[₹%*tF=~§]?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)$',
                    next_l
                )
                if m:
                    raw_s = m.group(1).replace(',', '')
                    if len(raw_s) >= 3 and raw_s[0] in ('2', '7') and not '.' in raw_s:
                        try:
                            val = float(raw_s[1:])
                            if 0.5 <= val <= 1_000_000:
                                candidates.append((val, f"₹{val:,.2f}", 13))
                        except ValueError:
                            pass
                    else:
                        try:
                            val = float(raw_s)
                            if 0.5 <= val <= 1_000_000:
                                candidates.append((val, f"₹{val:,.2f}", 10))
                        except ValueError:
                            pass

    # Strategy 4 — Standalone numeric line
    for line in lines:
        if _looks_like_date_line(line):
            continue
        cleaned = re.sub(r'[\s@#*~|<]+', ' ', line).strip()
        m = re.fullmatch(
            r'([₹%*tF=~§]|Rs\.?|INR)?\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)',
            cleaned, re.IGNORECASE
        )
        if m:
            num_str = m.group(2).replace(',', '')
            try:
                val = float(num_str)
                if val in range(2020, 2036) and any(str(int(val)) in l for l in lines if l != line):
                    continue
                if 0.5 <= val <= 1_000_000 and len(num_str.split('.')[0]) <= 7:
                    has_curr = bool(m.group(1))
                    has_dec = '.' in num_str
                    weight = 8 if has_curr else (6 if has_dec else 5)
                    candidates.append((val, f"₹{val:,.2f}", weight))
            except ValueError:
                pass

    if candidates:
        candidates.sort(key=lambda c: c[2], reverse=True)
        return candidates[0][1], candidates[0][0]
    return None, None


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

_DATE_TIME_ON = re.compile(
    r'\b(?:\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm))\s+on\s+(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
    re.IGNORECASE,
)
_DATE_TEXT = re.compile(
    r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\s+\d{4})(?:,\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm))?\b',
    re.IGNORECASE,
)
_DATE_ISO = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
_DATE_SLASH = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')
_PHONEPE_TXN_DATE = re.compile(r'\bT(\d{2})(\d{2})(\d{2})\d{12,18}\b')


def parse_date(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Returns (display "12 Mar 2026", iso "2026-03-12") or (None, None)."""
    m_on = _DATE_TIME_ON.search(text)
    if m_on:
        date_text = re.sub(r'\bSept\b', 'Sep', m_on.group(1), flags=re.IGNORECASE)
        for fmt in ("%d %b %Y", "%d %B %Y"):
            try:
                dt = datetime.strptime(date_text, fmt)
                return dt.strftime("%d %b %Y"), dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

    m = _DATE_TEXT.search(text)
    if m:
        date_text = re.sub(r'\bSept\b', 'Sep', m.group(1), flags=re.IGNORECASE)
        for fmt in ("%d %b %Y", "%d %B %Y"):
            try:
                dt = datetime.strptime(date_text, fmt)
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

    m_pe = _PHONEPE_TXN_DATE.search(text)
    if m_pe:
        try:
            yy = int(m_pe.group(1))
            mm = int(m_pe.group(2))
            dd = int(m_pe.group(3))
            year = 2000 + yy
            dt = datetime(year, mm, dd)
            return dt.strftime("%d %b %Y"), dt.strftime("%Y-%m-%d")
        except (ValueError, OverflowError):
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

_UTR_12DIGIT_CTX = re.compile(
    r'(?:UPI\s*(?:Ref|Transaction\s*ID|Reference|Ref\s*\(UTR\))|UTR\s*Number|UTR)'
    r'[:\s\(\)]*(\d{12})\b',
    re.IGNORECASE,
)
_UTR_CONTEXT = re.compile(
    r'(?:UPI\s*(?:Ref|Transaction\s*ID|Reference|Ref\s*\(UTR\))|UTR\s*Number|UTR|Transaction\s*ID)'
    r'[:\s\(\)]*([A-Za-z0-9]{6,25})',
    re.IGNORECASE,
)
_UTR_12DIGIT = re.compile(r'\b(\d{12})\b')
_UTR_ALPHA = re.compile(r'\b(UTR[A-Za-z0-9]{5,15})\b', re.IGNORECASE)


def parse_utr(text: str) -> Optional[str]:
    """Extracts 12-digit UTR or alphanumeric transaction IDs."""
    m = _UTR_12DIGIT_CTX.search(text)
    if m:
        return m.group(1).strip()

    m = _UTR_CONTEXT.search(text)
    if m:
        val = re.sub(r'[^A-Za-z0-9]', '', m.group(1))
        m12 = re.search(r'\b(\d{12})\b', val)
        if m12:
            return m12.group(1)
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
    if any(k in tl for k in ["quickpe", "uckpe", "uclpe", "ucipe", "quick pe"]):
        return "QuickPe"
    if "unipay" in tl or "uni pay" in tl:
        return "UniPay"
    if any(k in tl for k in ["google pay", "gpay", "g pay", "cicag"]):
        return "GooglePay"
    if "phonepe" in tl or "phone pe" in tl:
        return "PhonePe"
    if "paytm" in tl:
        return "Paytm"
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


def _clean_recipient(s: str) -> str:
    cleaned = re.sub(r'[\s@#*~|<]+', ' ', s).strip(" :-\t—")
    # Strip leading @ or icons
    cleaned = re.sub(r'^[@\s]+', '', cleaned)
    # Strip trailing currency symbol and amount without eating letters of names (e.g. REDBUS or Vittechnovit)
    cleaned = re.sub(r'(?:(?<![A-Za-z])[Ft]|[₹%*~=§27]|Rs\.?|INR)?\s*[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?$', '', cleaned).strip(" :-\t—")
    return cleaned


def parse_recipient(text: str) -> Optional[str]:
    tl = text.lower()
    for rec in _KNOWN_RECIPIENTS:
        if rec.lower() in tl:
            return rec
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        lower_line = line.lower()
        for prefix in ("paid to", "paid to:", "received from", "received from:", "to recipient", "transfer to", "recipient name", "recipient"):
            if prefix in lower_line:
                cleaned = re.sub(re.escape(prefix), '', line, flags=re.IGNORECASE).strip(": \t-—")
                cleaned = _clean_recipient(cleaned)
                if cleaned and len(cleaned) > 2:
                    return cleaned
                if i + 1 < len(lines):
                    next_line = _clean_recipient(lines[i + 1].strip())
                    if next_line and not any(k in next_line.lower() for k in ("amount", "paid from", "ref", "date", "status")):
                        return next_line
        for prefix in ("to:", "to "):
            if lower_line.startswith(prefix):
                cleaned = _clean_recipient(line[len(prefix):])
                if cleaned and len(cleaned) > 2 and not any(k in cleaned.lower() for k in ("nirmala", "@")):
                    return cleaned
                if cleaned and len(cleaned) > 2:
                    return cleaned
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
