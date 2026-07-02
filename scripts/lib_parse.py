"""
Deterministic parsing primitives for EN 15804 concrete EPDs.
The whole point: pull GWP table cells WITH provenance and a verbatim `raw` string,
never transcribing by eye. Handles the traps documented in RISKS.md:
 - decimal comma (EPD HUB) vs decimal point (IES/Australasia)
 - Unicode minus U+2010 '‐' on negative module-D credits
 - scientific E-notation, ND / NR / MND / blank vs declared-zero 0.00E+00
 - column->module mapping via x-coordinates (not text order)
"""
import re

# Canonical lifecycle modules in EN 15804 order (results tables use single D).
MODULE_ORDER = ["A1", "A2", "A3", "A1-A3", "A4", "A5",
                "B1", "B2", "B3", "B4", "B5", "B6", "B7",
                "C1", "C2", "C3", "C4", "D"]
MODULE_SET = set(MODULE_ORDER)

UNICODE_MINUS = ["‐", "‑", "‒", "–", "—", "−"]  # hyphen/dash/minus variants

# What a value cell can say when it is NOT a plain number.
STATUS_TOKENS = {
    "ND": "not_declared",
    "MND": "not_declared",
    "MNR": "not_relevant",
    "NR": "not_relevant",
    "NA": "not_declared",
    "N/A": "not_declared",
    "INA": "not_declared",   # "included in another module"-style markers vary; treat conservatively
    "-": "missing",
    "": "missing",
}

# tokens that look like scientific / decimal numbers (either decimal style)
NUM_RE = re.compile(r"^[+\-]?\d{1,3}([.,]\d+)?([eE][+\-]?\d+)?$")


def normalize_minus(s: str) -> str:
    for m in UNICODE_MINUS:
        s = s.replace(m, "-")
    return s


def classify_cell(raw: str):
    """Return (value_or_None, status, cleaned_raw). Never invents a number."""
    if raw is None:
        return None, "missing", ""
    raw_stripped = raw.strip()
    cleaned = normalize_minus(raw_stripped)
    key = cleaned.upper().strip()
    if key in STATUS_TOKENS:
        return None, STATUS_TOKENS[key], raw_stripped
    # numeric?
    token = cleaned.replace(" ", "")
    # decimal-comma -> decimal-point (safe: EPD number cells never use ',' as thousands sep here)
    token_pt = token.replace(",", ".")
    if NUM_RE.match(token_pt):
        try:
            val = float(token_pt)
        except ValueError:
            return None, "unparseable", raw_stripped
        status = "declared_zero" if val == 0.0 else "declared"
        return val, status, raw_stripped
    return None, "unparseable", raw_stripped


def parse_number(raw):
    v, _, _ = classify_cell(raw)
    return v
